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
Simple redis storage.
"""

from __future__ import absolute_import

import json

from datetime import datetime
from ast import literal_eval
from flask_track_usage.storage import Storage


class _RedisStorage(Storage):
    """
    Parent storage class for Redis storage.
    """

    def store(self, data):
        """
        Executed on "function call".

        :Parameters:
           - `data`: Data to store.
        """
        user_agent = data['user_agent']
        utcdatetime = datetime.fromtimestamp(data['date'])
        d = {
            'url': data['url'],
            'ua_browser': user_agent.browser or "",
            'ua_language': user_agent.language or "",
            'ua_platform': user_agent.platform or "",
            'ua_version': user_agent.version or "",
            'blueprint': data["blueprint"] or "",
            'view_args': json.dumps(data["view_args"], ensure_ascii=False),
            'status': data["status"] or "",
            'remote_addr': data["remote_addr"] or "",
            'authorization': data["authorization"] or "",
            'ip_info': data["ip_info"] or "",
            'path': data["path"] or "",
            'speed': data["speed"] or "",
            'datetime': str(utcdatetime) or ""
        }
        struct_name = self._construct_struct_name(utcdatetime)
        # create a set which will be used as an index, in order not to use
        # redis> keys <pattern>
        # Always try to add to avoid a network call
        self.db.sadd("usage_data_keys", struct_name)
        previous = len(self.db.hkeys(struct_name))
        self.db.hset(struct_name, previous + 1, d)

    def _get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        """
        Implements the simple usage information by criteria in a standard form.

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page
        """
        struct_name_start = self._construct_struct_name(
            start_date or datetime.now())
        struct_name_end = self._construct_struct_name(
            end_date or datetime(1970, 1, 1, 0, 0, 0))

        # make a pattern that looks like usage_data:20160*
        stop = self._pattern_stop(struct_name_start, struct_name_end)
        pattern = self._pattern(struct_name_start, stop)
        (response, keys) = self.db.sscan("usage_data_keys", 0, pattern,
                                         count=limit)

        data = [self.db.hgetall(key) for key in keys]
        # TODO: pipeline data request
        items = []
        for d in data:
            for item in d.values():
                try:
                    # skip items when errors occur
                    items.append(literal_eval(item))
                except:
                    continue
        return items

    @staticmethod
    def _construct_struct_name(date):
        """
        Construct a name based on a given date, that will be used as a key
        identifier.

        :Parameters:
           - `date`: Date to use as part of the construct key.
        """
        # Strip away the - from the date
        tmp = "".join(str(date.date()).rsplit("-"))

        # save the data in a hash set with this format:
        # usage_data:20180316 1 your-data
        return "usage_data:{0}".format(tmp)

    @staticmethod
    def _pattern_stop(date1, date2):
        """
        Find where there is a difference in the pattern.

        :Parameters:
           - `date1`: First datetime instance to compare.
           - `date2`: Second datetime instance to compare.
        """
        for i in xrange(len(date1)):
            if date1[i] != date2[i]:
                return i
        return -1

    @staticmethod
    def _pattern(date, stop):
        """Generate a pattern based on a date and when the date should stop,
        e.g. 201607*, in this case it excludes the day"""
        return "".join(date[:stop]) + "*"


class RedisStorage(_RedisStorage):
    """
    Creates it's own connection for storage.

    .. versionadded:: 1.1.1
    """

    def set_up(self, host='127.0.0.1', port=6379, password=None):
        """
        Sets up redis and checks that you have connected to it.

        :Parameters:
           - `host`: Host to conenct to. Default: 127.0.0.1
           - `port`: Port to connect to. Default: 27017
           - `password`: Optional password to authenticate with.
        """
        from redis import Redis
        self.db = Redis.from_url("redis://{0}:{1}".format(host, str(port)))
        assert self.db is not None
        assert self.db.ping() is True
