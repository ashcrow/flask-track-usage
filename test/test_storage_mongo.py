# Copyright (c) 2013 Steve Milner
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
Tests mongodb based storage.
"""

import datetime
import unittest

COLLECTION = False
HAS_PYMONGO = False

try:
    import pymongo
    HAS_PYMONGO = True
    DB = 'test'
    COLL_NAME = 'flask_track_usage'
    COLLECTION = getattr(getattr(pymongo.MongoClient(), DB), COLL_NAME)
except ImportError:
    HAS_PYMONGO = False
except pymongo.errors.ConnectionFailure:
    COLLECTION = False

from flask_track_usage import TrackUsage
from flask_track_usage.storage.mongo import MongoPiggybackStorage, MongoStorage

from . import FlaskTrackUsageTestCase


@unittest.skipUnless(HAS_PYMONGO, "Requires pymongo")
@unittest.skipUnless(COLLECTION, "Requires a running test MongoDB")
class TestMongoPiggybaclStorage(FlaskTrackUsageTestCase):
    """
    Tests MongoDB storage while using a piggybacked connection.
    """

    def setUp(self):
        """
        Set up an app to test with.
        """
        FlaskTrackUsageTestCase.setUp(self)
        self.storage = MongoPiggybackStorage(collection=COLLECTION)
        # Clean out the storage
        self.storage.collection.drop()
        self.track_usage = TrackUsage(self.app, self.storage)

    def test_mongo_piggyback_storage(self):
        """
        Test MongoPiggybackStorage stores the data the way we expect.
        """
        self.client.get('/')
        result = self.storage.collection.find_one()
        assert result['blueprint'] is None
        assert result['ip_info'] is None
        assert result['status'] == 200
        assert result['remote_addr'] is None  # because of testing
        assert result['speed'].__class__ is float
        assert result['view_args'] == {}
        assert result['url'] == 'http://localhost/'
        assert result['authorization'] is False
        assert result['user_agent']['browser'] is None  # because of testing
        assert result['user_agent']['platform'] is None  # because of testing
        assert result['user_agent']['language'] is None  # because of testing
        assert result['user_agent']['version'] is None  # because of testing
        assert result['path'] == '/'
        assert type(result['date']) is datetime.datetime


@unittest.skipUnless(HAS_PYMONGO, "Requires pymongo")
@unittest.skipUnless(COLLECTION, "Requires a running test MongoDB")
class TestMongoStorage(FlaskTrackUsageTestCase):
    """
    Tests MongoDB storage while using it's own connection.
    """

    def setUp(self):
        """
        Set up an app to test with.
        """
        FlaskTrackUsageTestCase.setUp(self)
        self.storage = MongoStorage(
            database=DB,
            collection=COLL_NAME
        )
        # Clean out the storage
        self.storage.collection.drop()
        self.track_usage = TrackUsage(self.app, self.storage)

    def test_mongo_storage_data(self):
        """
        Test that data is stored in MongoDB and retrieved correctly.
        """
        self.client.get('/')
        result = self.storage.collection.find_one()
        assert result['blueprint'] is None
        assert result['ip_info'] is None
        assert result['status'] == 200
        assert result['remote_addr'] is None  # because of testing
        assert result['speed'].__class__ is float
        assert result['view_args'] == {}
        assert result['url'] == 'http://localhost/'
        assert result['authorization'] is False
        assert result['user_agent']['browser'] is None  # because of testing
        assert result['user_agent']['platform'] is None  # because of testing
        assert result['user_agent']['language'] is None  # because of testing
        assert result['user_agent']['version'] is None  # because of testing
        assert result['path'] == '/'
        assert type(result['date']) is datetime.datetime

    def test_mongo_storage_get_usage(self):
        """
        Verify we can get usage information in expected ways.
        """
        # Make 3 requests to make sure we have enough records
        self.client.get('/')
        self.client.get('/')
        self.client.get('/')

        # Limit tests
        assert len(self.storage.get_usage()) == 3
        assert len(self.storage.get_usage(limit=2)) == 2
        assert len(self.storage.get_usage(limit=1)) == 1

        # Page tests
        assert len(self.storage.get_usage(limit=2, page=1)) == 2
        assert len(self.storage.get_usage(limit=2, page=2)) == 1

        # timing tests
        now = datetime.datetime.utcnow()
        assert len(self.storage.get_usage(start_date=now)) == 0
        assert len(self.storage.get_usage(end_date=now)) == 3
        assert len(self.storage.get_usage(end_date=now, limit=2)) == 2
