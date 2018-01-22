# Copyright (c) 2018 John Dupuy
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
MongoEngine storage.
"""

import datetime
import mongoengine as db

from flask_track_usage.storage.mongo import _MongoStorage


class UserAgent(db.EmbeddedDocument):
    browser = db.StringField()
    language = db.StringField()
    platform = db.StringField()
    version = db.StringField()


class UsageTracker(db.Document):
    date = db.DateTimeField(required=True, default=datetime.datetime.now)
    website = db.StringField(required=True, default="default")
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
    user_agent = db.EmbeddedDocumentField(UserAgent)

    meta = {
        'collection': "usageTracking"
    }


class MongoEngineStorage(_MongoStorage):
    """
    Uses a MongoEngine class to store data.
    """

    collection = UsageTracker

    def set_up(self, doc=None, website=None):
        """
        Sets the collection name and website "grouping".

        :Parameters:
           - `collection_name`: name for the MongoDB collection. Defaults to "usageTracking".
           - 'website': name for the website. Defaults to 'default'. Useful when multiple websites are
             saving data to the same collection.
        """
        self.collection = doc or UsageTracker
        self.website = website or 'default'

    def store(self, data):
        doc = self.collection()
        doc.date = datetime.datetime.fromtimestamp(data['date'])
        doc.website = self.website
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
        ua = UserAgent()
        ua.browser = str(data['user_agent'].browser)
        if data['user_agent'].language:
            ua.language = data['user_agent'].language
        ua.platform = data['user_agent'].platform
        if data['user_agent'].version:
            ua.version = str(data['user_agent'].version)
        doc.user_agent = ua
        doc.save()
        return doc  # this is used by any 'post' tracker function

#eof
