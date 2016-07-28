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
Simple couchdb storage.
"""
from __future__ import absolute_import

import json

from flask_track_usage.storage import Storage

from datetime import datetime
try:
    from couchdb.mapping import Document, TextField, IntegerField,\
        DateTimeField, FloatField, BooleanField, ViewField

    class UsageData(Document):
        """
        Document that represents the stored data.
        """
        url = TextField()
        ua_browser = TextField()
        ua_language = TextField()
        ua_platform = TextField()
        ua_version = TextField()
        blueprint = TextField()
        view_args = TextField()
        status = IntegerField()
        remote_addr = TextField()
        authorization = BooleanField()
        ip_info = TextField()
        path = TextField()
        speed = FloatField()
        datetime = DateTimeField(default=datetime.now)
        by_date = ViewField('start-end', '''function(doc, req) {
            if (!doc._conflicts) {
                emit(doc.datetime, doc);
            }
        }''')

except ImportError:
    pass


class _CouchDBStorage(Storage):
    """
    Parent storage class for CouchDB storage.
    """

    def store(self, data):
        """
        Executed on "function call".

        :Parameters:
           - `data`: Data to store.
        """
        user_agent = data['user_agent']
        utcdatetime = datetime.fromtimestamp(data['date'])
        usage_data = UsageData(url=data['url'],
                               ua_browser=user_agent.browser,
                               ua_language=user_agent.language,
                               ua_platform=user_agent.platform,
                               ua_version=user_agent.version,
                               blueprint=data["blueprint"],
                               view_args=json.dumps(data["view_args"],
                                                    ensure_ascii=False),
                               status=data["status"],
                               remote_addr=data["remote_addr"],
                               authorization=data["authorization"],
                               ip_info=data["ip_info"],
                               path=data["path"],
                               speed=data["speed"],
                               datetime=utcdatetime)
        usage_data.store(self.db)

    def _get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        """
        Implements the simple usage information by criteria in a standard form.

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page
        """
        UsageData.by_date.sync(self.db)
        data = self.db.query(UsageData.by_date.map_fun,
                             startkey=str(start_date), endkey=str(end_date),
                             limit=limit)
        return [row.value for row in data]


class CouchDBStorage(_CouchDBStorage):
    """
    Creates it's own connection for storage.

    .. versionadded:: 1.1.1
    """

    def set_up(self, database, host='127.0.0.1', port=5984,
               protocol='http', username=None, password=None):
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
        import couchdb
        from couchdb.http import PreconditionFailed
        self.connection = couchdb.Server("{0}://{1}:{2}".format(protocol,
                                                                host, port))
        try:
            self.db = self.connection.create(database)
        except PreconditionFailed as e:
            self.db = self.connection[database]
            print e
