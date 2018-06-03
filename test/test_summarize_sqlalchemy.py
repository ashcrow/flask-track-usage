# Copyright (c) 2013-2018 Steve Milner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     (1) Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#     (2) Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
#     (3)The name of the author may not be used to
#     endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
Tests sql based summarization.
"""

import datetime
import unittest


try:
    import sqlalchemy as sql
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


import datetime
import unittest
from flask import Blueprint
from test import FlaskTrackUsageTestCase
from flask_track_usage import TrackUsage
from flask_track_usage.storage.sql import SQLStorage
from flask_track_usage.summarization import (
    sumUrl,
    sumRemote,
    sumUserAgent,
    sumLanguage,
    sumServer,
)



@unittest.skipUnless(HAS_SQLALCHEMY, "Requires SQLAlchemy")
@unittest.skipUnless(HAS_POSTGRES, "Requires psycopg2 Postgres package")
class TestPostgreStorage(FlaskTrackUsageTestCase):

    def _create_storage(self):
        engine = sql.create_engine(
                "postgresql+psycopg2://postgres:@localhost/track_usage_test")
        metadata = sql.MetaData(bind=engine)
        self.storage = SQLStorage(
            engine=engine,
            metadata=metadata,
            table_name=self.given_table_name,
            hooks=[
                sumUrl,
                sumRemote,
                sumUserAgent,
                sumLanguage,
                sumServer
            ]
        )
        metadata.create_all()

    def setUp(self):
        self.given_table_name = 'my_usage'
        FlaskTrackUsageTestCase.setUp(self)
        self.blueprint = Blueprint('blueprint', __name__)

        @self.blueprint.route('/blueprint')
        def blueprint():
            return "blueprint"
        self.app.register_blueprint(self.blueprint)

        self._create_storage()

        self.fake_time  = datetime.datetime(2018, 4, 15, 9, 45, 12)  # Apr 15, 2018 at 9:45:12 AM UTC
        self.fake_hour  = datetime.datetime(2018, 4, 15, 9,  0,  0)  # Apr 15, 2018 at 9:00:00 AM UTC
        self.fake_day   = datetime.datetime(2018, 4, 15, 0,  0,  0)  # Apr 15, 2018 at 0:00:00 AM UTC
        self.fake_month = datetime.datetime(2018, 4,  1, 0,  0,  0)  # Apr  1, 2018 at 0:00:00 AM UTC

        self.track_usage = TrackUsage(
            self.app,
            self.storage,
            _fake_time=self.fake_time
        )
        self.track_usage.include_blueprint(self.blueprint)

    def tearDown(self):
        meta = sql.MetaData()
        meta.reflect(bind=self.storage._eng)
        for table in reversed(meta.sorted_tables):
            self.storage._eng.execute(table.delete())

    def test_table_names(self):
        meta = sql.MetaData()
        meta.reflect(bind=self.storage._eng)
        print(meta.tables.keys())
        self.assertIn('my_usage_language_hourly', meta.tables.keys())
        self.assertIn('my_usage_remote_monthly', meta.tables.keys())
        self.assertIn('my_usage_language_monthly', meta.tables.keys())
        self.assertIn('my_usage_url_monthly', meta.tables.keys())
        self.assertIn('my_usage_useragent_hourly', meta.tables.keys())
        self.assertIn('my_usage_server_hourly', meta.tables.keys())
        self.assertIn('my_usage_remote_hourly', meta.tables.keys())
        self.assertIn('my_usage_remote_daily', meta.tables.keys())
        self.assertIn('my_usage_language_daily', meta.tables.keys())
        self.assertIn('my_usage_url_hourly', meta.tables.keys())
        self.assertIn('my_usage_useragent_monthly', meta.tables.keys())
        self.assertIn('my_usage_useragent_daily', meta.tables.keys())
        self.assertIn('my_usage_url_daily', meta.tables.keys())
        self.assertIn('my_usage_server_daily', meta.tables.keys())
        self.assertIn('my_usage_server_monthly', meta.tables.keys())

    def test_basic_suite(self):
        self.client.get('/')  # call 3 times to make sure upsert works
        self.client.get('/')
        self.client.get('/')
        con = self.storage._eng.connect()

        # URL

        table = self.storage.sum_tables["url_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] == u'http://localhost/'
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["url_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] == u'http://localhost/'
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["url_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] == u'http://localhost/'
        assert result[2] == 3
        assert result[3] == 18

        # REMOTE IP

        table = self.storage.sum_tables["remote_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] == "127.0.0.1"
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["remote_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] == "127.0.0.1"
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["remote_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] == "127.0.0.1"
        assert result[2] == 3
        assert result[3] == 18

        # USER AGENT

        table = self.storage.sum_tables["useragent_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1].startswith("werkzeug/")
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["useragent_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1].startswith("werkzeug/")
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["useragent_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1].startswith("werkzeug/")
        assert result[2] == 3
        assert result[3] == 18

        # LANGUAGE

        table = self.storage.sum_tables["language_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] is None  # the werkzeug test client does not have a language
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["language_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] is None
        assert result[2] == 3
        assert result[3] == 18


        table = self.storage.sum_tables["language_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] is None
        assert result[2] == 3
        assert result[3] == 18

        # WHOLE SERVER

        table = self.storage.sum_tables["server_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] == self.app.name
        assert result[2] == 3
        assert result[3] == 18


        table = self.storage.sum_tables["server_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] == self.app.name
        assert result[2] == 3
        assert result[3] == 18

        table = self.storage.sum_tables["server_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.date==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] == self.app.name
        assert result[2] == 3
        assert result[3] == 18
