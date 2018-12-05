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
Simple mongodb storage.
"""

import datetime
import inspect

from flask_track_usage.storage import Storage


class _MongoStorage(Storage):
    """
    Parent storage class for Mongo storage.
    """

    def store(self, data):
        """
        Executed on "function call".

        :Parameters:
           - `data`: Data to store.

        .. versionchanged:: 1.1.0
           xforwardfor item added directly after remote_addr
        """
        ua_dict = {
            'browser': data['user_agent'].browser,
            'language': data['user_agent'].language,
            'platform': data['user_agent'].platform,
            'version': data['user_agent'].version,
        }
        data['date'] = datetime.datetime.fromtimestamp(data['date'])
        data['user_agent'] = ua_dict
        print(self.collection.insert(data))

    def _get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        """
        Implements the simple usage information by criteria in a standard form.

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page

        .. versionchanged:: 1.1.0
           xforwardfor item added directly after remote_addr
        """
        criteria = {}

        # Set up date based criteria
        if start_date or end_date:
            criteria['date'] = {}
            if start_date:
                criteria['date']['$gte'] = start_date
            if end_date:
                criteria['date']['$lte'] = end_date

        cursor = []
        if limit:
            cursor = self.collection.find(criteria).skip(
                limit * (page - 1)).limit(limit)
        else:
            cursor = self.collection.find(criteria)
        return [x for x in cursor]


class MongoPiggybackStorage(_MongoStorage):
    """
    Uses a pymongo collection to store data.
    """

    def set_up(self, collection, hooks=None):
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
            port=27017, username=None, password=None, hooks=None):
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
        self.connection = pymongo.MongoClient(host, port)
        self.db = getattr(self.connection, database)
        if username and password:
            self.db.authenticate(username, password)
        self.collection = getattr(self.db, collection)


class MongoEngineStorage(_MongoStorage):
    """
    Uses MongoEngine library to store data in MongoDB.

    The resulting collection is named `usageTracking`.

    Should you need to access the actual Document class that this storage uses,
    you can pull it from `collection` *instance* attribute. For example: ::

    trackerDoc = MongoEngineStorage().collection
    """

    def set_up(self, doc=None, website=None, apache_log=False, hooks=None):
        import mongoengine as db
        """
        Sets the general settings.

        :Parameters:
           - `doc`: optional alternate MongoEngine document class.
           - 'website': name for the website. Defaults to 'default'. Useful
             when multiple websites are saving data to the same collection.
           - 'apache_log': if set to True, then an attribute called
             'apache_combined_log' is set that mimics a line from a traditional
             apache webserver web log text file.

        .. versionchanged:: 2.0.0
        """

        class UserAgent(db.EmbeddedDocument):
            browser = db.StringField()
            language = db.StringField()
            platform = db.StringField()
            version = db.StringField()
            string = db.StringField()

        class UsageTracker(db.Document):
            date = db.DateTimeField(
                required=True,
                default=datetime.datetime.utcnow
            )
            website = db.StringField(required=True, default="default")
            server_name = db.StringField(default="self")
            blueprint = db.StringField(default=None)
            view_args = db.DictField()
            ip_info = db.StringField()
            xforwardedfor = db.StringField()
            path = db.StringField()
            speed = db.FloatField()
            remote_addr = db.StringField()
            url = db.StringField()
            status = db.IntField()
            authorization = db.BooleanField()
            content_length = db.IntField()
            url_args = db.DictField()
            username = db.StringField()
            user_agent = db.EmbeddedDocumentField(UserAgent)
            track_var = db.DictField()
            apache_combined_log = db.StringField()
            meta = {
                'collection': "usageTracking"
            }

        self.collection = doc or UsageTracker
        # self.user_agent = UserAgent
        self.website = website or 'default'
        self.apache_log = apache_log

    def store(self, data):
        doc = self.collection()
        doc.date = datetime.datetime.fromtimestamp(data['date'])
        doc.website = self.website
        doc.server_name = data['server_name']
        doc.blueprint = data['blueprint']
        doc.view_args = data['view_args']
        doc.ip_info = data['ip_info']
        doc.xforwardedfor = data['xforwardedfor']
        doc.path = data['path']
        doc.speed = data['speed']
        doc.remote_addr = data['remote_addr']
        doc.url = data['url']
        doc.status = data['status']
        doc.authorization = data['authorization']
        doc.content_length = data['content_length']
        doc.url_args = data['url_args']
        doc.username = data['username']
        doc.track_var = data['track_var']
        # the following is VERY MUCH A HACK to allow a passed 'doc' on set_up
        ua = doc._fields['user_agent'].document_type_obj()
        ua.browser = data['user_agent'].browser
        if data['user_agent'].language:
            ua.language = data['user_agent'].language
        ua.platform = data['user_agent'].platform
        if data['user_agent'].version:
            ua.version = str(data['user_agent'].version)
        ua.string = data['user_agent'].string
        doc.user_agent = ua
        if self.apache_log:
            t = '{h} - {u} [{t}] "{r}" {s} {b} "{ref}" "{ua}"'.format(
                h=data['remote_addr'],
                u=data["username"] or '-',
                t=doc.date.strftime("%d/%b/%Y:%H:%M:%S %z"),
                r=data.get("request", '?'),
                s=data['status'],
                b=data['content_length'],
                ref=data['url'],
                ua=str(data['user_agent'])
            )
            doc.apache_combined_log = t
        doc.save()
        data['mongoengine_document'] = doc
        return data

    def _get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        """
        Implements the simple usage information by criteria in a standard form.

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page

        .. versionchanged:: 2.0.0
        """
        query = {}
        if start_date:
            query["date__gte"] = start_date
        if end_date:
            query["date__lte"] = end_date
        if limit:
            first = limit * (page - 1)
            last = limit * page
            logs = self.collection.objects(
                **query
            ).order_by('-date')[first:last]
        else:
            logs = self.collection.objects(**query).order_by('-date')
        result = [log.to_mongo().to_dict() for log in logs]
        return result

    def get_sum(
        self,
        hook,
        start_date=None,
        end_date=None,
        limit=500,
        page=1,
        target=None
    ):
        """
        Queries a subtending hook for summarization data.

        :Parameters:
           - 'hook': the hook 'class' or it's name as a string
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page
           - 'target': search string to limit results; meaning depend on hook


        .. versionchanged:: 2.0.0
        """
        if inspect.isclass(hook):
            hook_name = hook.__name__
        else:
            hook_name = str(hook)
        for h in self._post_storage_hooks:
            if h.__class__.__name__ == hook_name:
                return h.get_sum(
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                    page=page,
                    target=target,
                    _parent_class_name=self.__class__.__name__,
                    _parent_self=self
                )
        raise NotImplementedError(
            'Cannot find hook named "{}"'.format(hook_name)
        )
