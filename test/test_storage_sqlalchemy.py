# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 21:31:41 2014

@author: Goutham
"""

try:
    import sqlalchemy as sql
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    
import datetime
import unittest
from . import FlaskTrackUsageTestCase
from flask_track_usage import TrackUsage
from flask_track_usage.storage.sql import SQLStorage
    
@unittest.skipUnless(HAS_SQLALCHEMY, "Requires SQLAlchemy")
class TestSQLiteStorage(FlaskTrackUsageTestCase):
    def setUp(self):
        """
        Set up an app to test with.
        """
        FlaskTrackUsageTestCase.setUp(self)
        self.storage = SQLStorage(
            conn_str="sqlite://",
            table_name="my_usage"
        )
        # Clean out the storage
        
        self.track_usage = TrackUsage(self.app, self.storage)

    def test_sqlite_storage_data(self):
        """
        Test that data is stored in SQLite and retrieved correctly.
        """
        self.client.get('/')
        con = self.storage._eng.connect()
        s = sql.select([self.storage.track_table])
        result = con.execute(s).fetchone()
        #(1, u'http://localhost/', None, None, None, None, u'{}', 200, None, False, None, u'/', 0.0, datetime.datetime(2014, 3, 25, 4, 57, 19)
        assert result[0] == 1 # first row
        assert result[1] == u'http://localhost/'
        assert result[2] is None
        assert result[3] is None
        assert result[4] is None
        assert result[5] is None
        assert result[7] == 200
        assert result[8] is None
        assert result[9] == False
        assert result[10] is None
        assert result[11] == '/'
        assert result[12].__class__ is float
        assert type(result[13]) is datetime.datetime
        
    def test_sqlite_storage_get_usage(self):
        """
        Verify we can get usage information in expected ways using SQLStorages.
        """
        # Make 3 requests to make sure we have enough records
        self.client.get('/')
        self.client.get('/')
        self.client.get('/')

        # Limit tests
        assert len(self.storage.get_usage()) == 3
        assert len(self.storage.get_usage(limit=2)) == 2
        assert len(self.storage.get_usage(limit=1)) == 1
        
        # timing tests
        now = datetime.datetime.utcnow()
        assert len(self.storage.get_usage(start_date=now)) == 0
        assert len(self.storage.get_usage(end_date=now)) == 3
        assert len(self.storage.get_usage(end_date=now, limit=2)) == 2