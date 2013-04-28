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
Simple mongodb storage.
"""

import datetime

from flask_track_usage.storage import Storage


class _MongoStorage(Storage):

    def store(self, data):
        ua_dict = {
            'browser': data['user_agent'].browser,
            'language': data['user_agent'].language,
            'platform': data['user_agent'].platform,
            'version': data['user_agent'].version,
        }
        data['date'] = datetime.datetime.fromtimestamp(data['date'])
        data['user_agent'] = ua_dict
        self.collection.insert(data)


class MongoPiggybackStorage(_MongoStorage):
    """
    Uses a pymongo collection to store data.
    """

    def set_up(self, collection):
        """
        Sets the collection.

        :Parameters:
           - `collection`: A pymongo collection (not database or connection).
        """
        self.collection = collection


class MongoStorage(_MongoStorage):
    """
    Creates it's own connection for storage.
    """

    def set_up(
            self, database, collection, host='127.0.0.1',
            port=27017, username=None, password=None):
        """
        Sets the collection.

        :Parameters:
           - `database`: Name of the database to use.
           - `collection`: Name of the collection to use.
           - `host`: Host to conenct to. Default: 127.0.0.1
           - `port`: Port to connect to. Default: 27017
           - `username`: Optional username to authenticate with.
           - `password`: Optional password to authenticate with.
        """
        import pymongo
        self.connection = pymongo.Connection(host, port)
        self.db = getattr(self.connection, database)
        if username and password:
            self.db.authenticate(username, password)
        self.collection = getattr(self.db, collection)
