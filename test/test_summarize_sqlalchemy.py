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
                # sumUserAgent,
                # sumLanguage,
                # sumServer
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

        self.fake_time  = datetime.datetime(2018, 04, 15, 9, 45, 12)  # Apr 15, 2018 at 9:45:12 AM UTC
        self.fake_hour  = datetime.datetime(2018, 04, 15, 9,  0,  0)  # Apr 15, 2018 at 9:00:00 AM UTC
        self.fake_day   = datetime.datetime(2018, 04, 15, 0,  0,  0)  # Apr 15, 2018 at 0:00:00 AM UTC
        self.fake_month = datetime.datetime(2018, 04,  1, 0,  0,  0)  # Apr  1, 2018 at 0:00:00 AM UTC

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

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18

        # table = self.storage.sum_tables["url_hourly"]
        # s = sql \
        #     .select([table]) \
        #     .where(table.c.date==self.fake_hour)
        # result = con.execute(s).fetchone()
        # assert result is not None
        # assert result[0] == self.fake_hour
        # assert result[1] == u'http://localhost/'
        # assert result[2] == 3
        # assert result[3] == 18



# from flask_track_usage import TrackUsage
# # from flask_track_usage.storage.mongo import MongoEngineStorage
# from flask_track_usage.summarization import (
#     sumUrl,
#     sumRemote,
#     sumUserAgent,
#     sumLanguage,
#     sumServer,
# )

# # if HAS_MONGOENGINE:
# #     from flask_track_usage.summarization.postgresqlstorage import (
# #         UsageTrackerSumUrlHourly,
# #         UsageTrackerSumUrlDaily,
# #         UsageTrackerSumUrlMonthly,
# #         UsageTrackerSumRemoteHourly,
# #         UsageTrackerSumRemoteDaily,
# #         UsageTrackerSumRemoteMonthly,
# #         UsageTrackerSumUserAgentHourly,
# #         UsageTrackerSumUserAgentDaily,
# #         UsageTrackerSumUserAgentMonthly,
# #         UsageTrackerSumLanguageHourly,
# #         UsageTrackerSumLanguageDaily,
# #         UsageTrackerSumLanguageMonthly,
# #         UsageTrackerSumServerHourly,
# #         UsageTrackerSumServerDaily,
# #         UsageTrackerSumServerMonthly,
# #     )

# from . import FlaskTrackUsageTestCase


# @unittest.skipUnless(HAS_MONGOENGINE, "Requires MongoEngine")
# class TestMongoEngineSummarizeBasic(FlaskTrackUsageTestCase):
#     """
#     Tests MongoEngine summaries.
#     """

#     def setUp(self):
#         """
#         Set up an app to test with.
#         """
#         FlaskTrackUsageTestCase.setUp(self)
#         self.storage = MongoEngineStorage(hooks=[
#             sumUrl,
#             sumRemote,
#             sumUserAgent,
#             sumLanguage,
#             sumServer
#         ])
#         self.track_usage = TrackUsage(self.app, self.storage)
#         # Clean out the summary
#         UsageTrackerSumUrlHourly.drop_collection()
#         UsageTrackerSumUrlDaily.drop_collection()
#         UsageTrackerSumUrlMonthly.drop_collection()
#         UsageTrackerSumRemoteHourly.drop_collection()
#         UsageTrackerSumRemoteDaily.drop_collection()
#         UsageTrackerSumRemoteMonthly.drop_collection()
#         UsageTrackerSumUserAgentHourly.drop_collection()
#         UsageTrackerSumUserAgentDaily.drop_collection()
#         UsageTrackerSumUserAgentMonthly.drop_collection()
#         UsageTrackerSumLanguageHourly.drop_collection()
#         UsageTrackerSumLanguageDaily.drop_collection()
#         UsageTrackerSumLanguageMonthly.drop_collection()
#         UsageTrackerSumServerHourly.drop_collection()
#         UsageTrackerSumServerDaily.drop_collection()
#         UsageTrackerSumServerMonthly.drop_collection()
#         # trigger one timed summary
#         self.now = datetime.datetime.utcnow()
#         self.hour = self.now.replace(minute=0, second=0, microsecond=0)
#         self.day = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
#         self.month = self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         self.client.get('/')

#     def test_postgresql_url_summary(self):
#         """
#         Test MongoEngine url summarization.
#         """
#         hour_doc = UsageTrackerSumUrlHourly.objects.first()
#         assert hour_doc.url == 'http://localhost/'
#         assert hour_doc.date == self.hour
#         assert hour_doc.hits == 1
#         assert hour_doc.transfer > 1
#         day_doc = UsageTrackerSumUrlDaily.objects.first()
#         assert day_doc.url == 'http://localhost/'
#         assert day_doc.date == self.day
#         assert day_doc.hits == 1
#         assert day_doc.transfer > 1
#         month_doc = UsageTrackerSumUrlMonthly.objects.first()
#         assert month_doc.url == 'http://localhost/'
#         assert month_doc.date == self.month
#         assert month_doc.hits == 1
#         assert month_doc.transfer > 1

    # def test_postgresql_remote_summary(self):
    #     """
    #     Test MongoEngine remote IP summarization.
    #     """
    #     hour_doc = UsageTrackerSumRemoteHourly.objects.first()
    #     assert hour_doc.remote_addr == '127.0.0.1'
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumRemoteDaily.objects.first()
    #     assert day_doc.remote_addr == '127.0.0.1'
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumRemoteMonthly.objects.first()
    #     assert month_doc.remote_addr == '127.0.0.1'
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

    # def test_postgresql_user_agent_summary(self):
    #     """
    #     Test MongoEngine User Agent summarization.
    #     """
    #     hour_doc = UsageTrackerSumUserAgentHourly.objects.first()
    #     assert hour_doc.user_agent_string.startswith("werkzeug/")
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumUserAgentDaily.objects.first()
    #     assert day_doc.user_agent_string.startswith("werkzeug/")
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumUserAgentMonthly.objects.first()
    #     assert month_doc.user_agent_string.startswith("werkzeug/")
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

    # def test_postgresql_language_summary(self):
    #     """
    #     Test MongoEngine Language summarization.
    #     """
    #     hour_doc = UsageTrackerSumLanguageHourly.objects.first()
    #     assert hour_doc.language == 'none'
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumLanguageDaily.objects.first()
    #     assert day_doc.language == 'none'
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumLanguageMonthly.objects.first()
    #     assert month_doc.language == 'none'
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

    # def test_postgresql_server_summary(self):
    #     """
    #     Test MongoEngine server summarization.
    #     """
    #     hour_doc = UsageTrackerSumServerHourly.objects.first()
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumServerDaily.objects.first()
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumServerMonthly.objects.first()
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

