
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


@unittest.skipUnless(HAS_MYSQL, "Requires mysql-python package")
@unittest.skipUnless((HAS_SQLALCHEMY), "Requires SQLAlchemy")
class TestMySQLStorage(FlaskTrackUsageTestCase):

    def _create_storage(self):
        if 'SQLALCHEMY_DATABASE_URI_TEST' in os.environ.keys():
            SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI_TEST']
        else:
            SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://travis@localhost/track_usage_test"

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
