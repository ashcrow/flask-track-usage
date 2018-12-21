
try:
    import sqlalchemy as sql
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

try:
    import _mysql
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

import datetime
import unittest
import json
import os
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

if 'SQLALCHEMY_DATABASE_URI_TEST' in os.environ.keys():
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI_TEST']
else:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://travis@localhost/track_usage_test"

@unittest.skipUnless(HAS_MYSQL, "Requires mysql-python package")
@unittest.skipUnless((HAS_SQLALCHEMY), "Requires SQLAlchemy")
class TestMySQLStorage(FlaskTrackUsageTestCase):

    def _create_storage(self):
        engine = sql.create_engine(SQLALCHEMY_DATABASE_URI)
        metadata = sql.MetaData(bind=engine)
        self.storage = SQLStorage(
            engine=engine,
            metadata=metadata,
            table_name=self.given_table_name
        )
        # metadata.create_all()

    def tearDown(self):
        """
        Delete the table
        """
        self.storage.track_table.drop(self.storage._eng)

    def setUp(self):
        """
        Create the app, track usage and init storage
        """
        self.given_table_name = 'my_usage'
        FlaskTrackUsageTestCase.setUp(self)
        self._create_storage()

        self.track_usage = TrackUsage()
        self.track_usage.init_app(self.app, self.storage)
        # self.track_usage.include_blueprint(self.blueprint)

    def test_table_name(self):
        meta = sql.MetaData()
        meta.reflect(bind=self.storage._eng)
        print(self.given_table_name, list(meta.tables.keys())[0])
        self.assertIn(self.given_table_name, meta.tables.keys())

    def test_storage_data_basic(self):
        self.client.get('/')
        result = self.storage.track_table.select().execute().first()
        assert result['id'] == 1  # first row
        assert result['url'] == u'http://localhost/'
        assert result['ua_browser'] is None
        assert result['ua_language'] is None
        assert result['ua_platform'] is None
        assert result['ua_version'] is None
        assert result['blueprint'] is None
        assert result['view_args'] == '{}'
        assert result['status'] == 200
        assert result['remote_addr'] == '127.0.0.1'
        assert result['xforwardedfor'] is None
        assert result['authorization'] is False
        assert result['ip_info'] is None
        assert result['path'] == '/'
        assert result['speed'] > 0
        assert type(result['datetime']) is datetime.datetime
        assert result['username'] is None
        assert result['track_var'] == '{}'

    def test_storage_get_usage_pagination(self):
        # test pagination
        for i in range(100):
            self.client.get('/')

        limit = 10
        num_pages = 10
        for page in range(1, num_pages + 1):
            result = self.storage._get_usage(limit=limit, page=page)
            assert len(result) == limit

        # actual api test
        result = self.storage._get_raw(limit=100)  # raw data
        result2 = self.storage.get_usage(limit=100)  # dict data
        for i in range(100):
            for key in result[i].keys():
                if key == 'id':
                    assert key not in result2[i]
                    assert key in result[i]
                elif 'ua_' in key:
                    result[i][key] == result2[i]['user_agent'][key.split('_')[1]]
                elif result[i][key] == '{}':
                    assert result2[i][key] is None
                else:
                    assert result[i][key] == result2[i][key]
        
    

@unittest.skipUnless(HAS_MYSQL, "Requires mysql-python package")
@unittest.skipUnless((HAS_SQLALCHEMY), "Requires SQLAlchemy")
class TestMySQLStorageSummary(FlaskTrackUsageTestCase):

    def _create_storage(self):
        engine = sql.create_engine(SQLALCHEMY_DATABASE_URI)
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
        # metadata.create_all()

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
            table.drop(self.storage._eng)

    def test_table_names(self):
        meta = sql.MetaData()
        meta.reflect(bind=self.storage._eng)
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

        # Test the get sum
        results = self.storage.get_sum('sumUrl')
        self.assertIn('url_hourly', results.keys())
        self.assertIn('url_daily', results.keys())
        self.assertIn('url_monthly', results.keys())

        assert len(results['url_hourly']) == 1
        assert len(results['url_daily']) == 1
        assert len(results['url_monthly']) == 1

        # URL

        table = self.storage.sum_tables["url_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] == u'http://localhost/'
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["url_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] == u'http://localhost/'
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["url_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] == u'http://localhost/'
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        # REMOTE IP

        table = self.storage.sum_tables["remote_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] == "127.0.0.1"
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["remote_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] == "127.0.0.1"
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["remote_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] == "127.0.0.1"
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        # USER AGENT

        table = self.storage.sum_tables["useragent_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1].startswith("werkzeug/")
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["useragent_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1].startswith("werkzeug/")
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["useragent_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1].startswith("werkzeug/")
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        # LANGUAGE

        table = self.storage.sum_tables["language_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] is None  # the werkzeug test client does not have a language
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["language_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] is None
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18


        table = self.storage.sum_tables["language_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] is None
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        # WHOLE SERVER

        table = self.storage.sum_tables["server_hourly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_hour)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_hour
        assert result[1] == self.app.name
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18


        table = self.storage.sum_tables["server_daily"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_day)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_day
        assert result[1] == self.app.name
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18

        table = self.storage.sum_tables["server_monthly"]
        s = sql \
            .select([table]) \
            .where(table.c.datetime==self.fake_month)
        result = con.execute(s).fetchone()
        assert result is not None
        assert result[0] == self.fake_month
        assert result[1] == self.app.name
        assert result[2] == '{}'
        assert result[3] == 3
        assert result[4] == 18
