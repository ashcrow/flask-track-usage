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
Tests mongodb based storage.
"""

import datetime
import unittest
import json


HAS_MONGOENGINE = False

try:
    import mongoengine
    import pprint
    HAS_MONGOENGINE = True
    try:
        mongoengine.connect(db="mongoenginetest")
    except:
        print('Can not connect to mongoengine database.')
        HAS_MONGOENGINE = False
except ImportError:
    pass

from flask_track_usage import TrackUsage
from flask_track_usage.storage.mongo import MongoEngineStorage
from flask_track_usage.summarization import (
    sumUrl,
    sumRemote,
    sumUserAgent,
    sumLanguage,
    sumServer,
)

if HAS_MONGOENGINE:
    from flask_track_usage.summarization.mongoenginestorage import (
        UsageTrackerSumUrlHourly,
        UsageTrackerSumUrlDaily,
        UsageTrackerSumUrlMonthly,
        UsageTrackerSumRemoteHourly,
        UsageTrackerSumRemoteDaily,
        UsageTrackerSumRemoteMonthly,
        UsageTrackerSumUserAgentHourly,
        UsageTrackerSumUserAgentDaily,
        UsageTrackerSumUserAgentMonthly,
        UsageTrackerSumLanguageHourly,
        UsageTrackerSumLanguageDaily,
        UsageTrackerSumLanguageMonthly,
        UsageTrackerSumServerHourly,
        UsageTrackerSumServerDaily,
        UsageTrackerSumServerMonthly,
    )

from . import FlaskTrackUsageTestCase


@unittest.skipUnless(HAS_MONGOENGINE, "Requires MongoEngine")
class TestMongoEngineSummarizeBasic(FlaskTrackUsageTestCase):
    """
    Tests MongoEngine summaries.
    """

    def setUp(self):
        """
        Set up an app to test with.
        """
        FlaskTrackUsageTestCase.setUp(self)
        self.storage = MongoEngineStorage(hooks=[
            sumUrl,
            sumRemote,
            sumUserAgent,
            sumLanguage,
            sumServer
        ])
        self.track_usage = TrackUsage(self.app, self.storage)
        # Clean out the summary
        UsageTrackerSumUrlHourly.drop_collection()
        UsageTrackerSumUrlDaily.drop_collection()
        UsageTrackerSumUrlMonthly.drop_collection()
        UsageTrackerSumRemoteHourly.drop_collection()
        UsageTrackerSumRemoteDaily.drop_collection()
        UsageTrackerSumRemoteMonthly.drop_collection()
        UsageTrackerSumUserAgentHourly.drop_collection()
        UsageTrackerSumUserAgentDaily.drop_collection()
        UsageTrackerSumUserAgentMonthly.drop_collection()
        UsageTrackerSumLanguageHourly.drop_collection()
        UsageTrackerSumLanguageDaily.drop_collection()
        UsageTrackerSumLanguageMonthly.drop_collection()
        UsageTrackerSumServerHourly.drop_collection()
        UsageTrackerSumServerDaily.drop_collection()
        UsageTrackerSumServerMonthly.drop_collection()
        # trigger one timed summary
        self.now = datetime.datetime.utcnow()
        self.hour = self.now.replace(minute=0, second=0, microsecond=0)
        self.day = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.month = self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.client.get('/')

    def test_mongoengine_url_summary(self):
        """
        Test MongoEngine url summarization.
        """
        hour_doc = UsageTrackerSumUrlHourly.objects.first()
        assert hour_doc.url == 'http://localhost/'
        assert hour_doc.date == self.hour
        assert hour_doc.hits == 1
        assert hour_doc.transfer > 1
        day_doc = UsageTrackerSumUrlDaily.objects.first()
        assert day_doc.url == 'http://localhost/'
        assert day_doc.date == self.day
        assert day_doc.hits == 1
        assert day_doc.transfer > 1
        month_doc = UsageTrackerSumUrlMonthly.objects.first()
        assert month_doc.url == 'http://localhost/'
        assert month_doc.date == self.month
        assert month_doc.hits == 1
        assert month_doc.transfer > 1

    def test_mongoengine_remote_summary(self):
        """
        Test MongoEngine remote IP summarization.
        """
        hour_doc = UsageTrackerSumRemoteHourly.objects.first()
        assert hour_doc.remote_addr == '127.0.0.1'
        assert hour_doc.date == self.hour
        assert hour_doc.hits == 1
        assert hour_doc.transfer > 1
        day_doc = UsageTrackerSumRemoteDaily.objects.first()
        assert day_doc.remote_addr == '127.0.0.1'
        assert day_doc.date == self.day
        assert day_doc.hits == 1
        assert day_doc.transfer > 1
        month_doc = UsageTrackerSumRemoteMonthly.objects.first()
        assert month_doc.remote_addr == '127.0.0.1'
        assert month_doc.date == self.month
        assert month_doc.hits == 1
        assert month_doc.transfer > 1

    def test_mongoengine_user_agent_summary(self):
        """
        Test MongoEngine User Agent summarization.
        """
        hour_doc = UsageTrackerSumUserAgentHourly.objects.first()
        assert hour_doc.user_agent_string.startswith("werkzeug/")
        assert hour_doc.date == self.hour
        assert hour_doc.hits == 1
        assert hour_doc.transfer > 1
        day_doc = UsageTrackerSumUserAgentDaily.objects.first()
        assert day_doc.user_agent_string.startswith("werkzeug/")
        assert day_doc.date == self.day
        assert day_doc.hits == 1
        assert day_doc.transfer > 1
        month_doc = UsageTrackerSumUserAgentMonthly.objects.first()
        assert month_doc.user_agent_string.startswith("werkzeug/")
        assert month_doc.date == self.month
        assert month_doc.hits == 1
        assert month_doc.transfer > 1

    def test_mongoengine_language_summary(self):
        """
        Test MongoEngine Language summarization.
        """
        hour_doc = UsageTrackerSumLanguageHourly.objects.first()
        assert hour_doc.language == 'none'
        assert hour_doc.date == self.hour
        assert hour_doc.hits == 1
        assert hour_doc.transfer > 1
        day_doc = UsageTrackerSumLanguageDaily.objects.first()
        assert day_doc.language == 'none'
        assert day_doc.date == self.day
        assert day_doc.hits == 1
        assert day_doc.transfer > 1
        month_doc = UsageTrackerSumLanguageMonthly.objects.first()
        assert month_doc.language == 'none'
        assert month_doc.date == self.month
        assert month_doc.hits == 1
        assert month_doc.transfer > 1

    def test_mongoengine_server_summary(self):
        """
        Test MongoEngine server summarization.
        """
        hour_doc = UsageTrackerSumServerHourly.objects.first()
        assert hour_doc.server_name == self.app.name
        assert hour_doc.date == self.hour
        assert hour_doc.hits == 1
        assert hour_doc.transfer > 1
        day_doc = UsageTrackerSumServerDaily.objects.first()
        assert day_doc.server_name == self.app.name
        assert day_doc.date == self.day
        assert day_doc.hits == 1
        assert day_doc.transfer > 1
        month_doc = UsageTrackerSumServerMonthly.objects.first()
        assert month_doc.server_name == self.app.name
        assert month_doc.date == self.month
        assert month_doc.hits == 1
        assert month_doc.transfer > 1


@unittest.skipUnless(HAS_MONGOENGINE, "Requires MongoEngine")
class TestMongoEngineSummarizeGetSum(FlaskTrackUsageTestCase):
    """
    Tests query of MongoEngine summaries.
    """

    def setUp(self):
        """
        Set up an app to test with.
        """
        self.fake_time1  = datetime.datetime(2018, 4, 15, 8, 45, 12)  # Apr 15, 2018 at 8:45:12 AM UTC
        self.fake_hour1  = datetime.datetime(2018, 4, 15, 8,  0,  0)  # Apr 15, 2018 at 8:00:00 AM UTC
        self.fake_day1   = datetime.datetime(2018, 4, 15, 0,  0,  0)  # Apr 15, 2018 at 0:00:00 AM UTC
        self.fake_month1 = datetime.datetime(2018, 4,  1, 0,  0,  0)  # Apr  1, 2018 at 0:00:00 AM UTC

        self.fake_time2  = datetime.datetime(2018, 4, 15, 9, 45, 12)  # Apr 15, 2018 at 9:45:12 AM UTC
        self.fake_hour2  = datetime.datetime(2018, 4, 15, 9,  0,  0)  # Apr 15, 2018 at 9:00:00 AM UTC
        self.fake_day2   = datetime.datetime(2018, 4, 15, 0,  0,  0)  # Apr 15, 2018 at 0:00:00 AM UTC
        self.fake_month2 = datetime.datetime(2018, 4,  1, 0,  0,  0)  # Apr  1, 2018 at 0:00:00 AM UTC

        self.fake_time3  = datetime.datetime(2018, 4, 16, 9, 45, 12)  # Apr 16, 2018 at 9:45:12 AM UTC
        self.fake_hour3  = datetime.datetime(2018, 4, 16, 9,  0,  0)  # Apr 16, 2018 at 9:00:00 AM UTC
        self.fake_day3   = datetime.datetime(2018, 4, 16, 0,  0,  0)  # Apr 16, 2018 at 0:00:00 AM UTC
        self.fake_month3 = datetime.datetime(2018, 4,  1, 0,  0,  0)  # Apr  1, 2018 at 0:00:00 AM UTC

        self.fake_time4  = datetime.datetime(2018, 5, 10, 9, 45, 12)  # May 10, 2018 at 9:45:12 AM UTC
        self.fake_hour4  = datetime.datetime(2018, 5, 10, 9,  0,  0)  # May 10, 2018 at 9:00:00 AM UTC
        self.fake_day4   = datetime.datetime(2018, 5, 10, 0,  0,  0)  # May 10, 2018 at 0:00:00 AM UTC
        self.fake_month4 = datetime.datetime(2018, 5,  1, 0,  0,  0)  # May  1, 2018 at 0:00:00 AM UTC

        FlaskTrackUsageTestCase.setUp(self)
        self.storage = MongoEngineStorage(hooks=[
            sumUrl,
            sumRemote,
            sumUserAgent,
            sumLanguage,
            sumServer
        ])
        self.track_usage = TrackUsage(
            self.app,
            self.storage,
            _fake_time = self.fake_time1
        )
        # Clean out the summary
        UsageTrackerSumUrlHourly.drop_collection()
        UsageTrackerSumUrlDaily.drop_collection()
        UsageTrackerSumUrlMonthly.drop_collection()
        UsageTrackerSumRemoteHourly.drop_collection()
        UsageTrackerSumRemoteDaily.drop_collection()
        UsageTrackerSumRemoteMonthly.drop_collection()
        UsageTrackerSumUserAgentHourly.drop_collection()
        UsageTrackerSumUserAgentDaily.drop_collection()
        UsageTrackerSumUserAgentMonthly.drop_collection()
        UsageTrackerSumLanguageHourly.drop_collection()
        UsageTrackerSumLanguageDaily.drop_collection()
        UsageTrackerSumLanguageMonthly.drop_collection()
        UsageTrackerSumServerHourly.drop_collection()
        UsageTrackerSumServerDaily.drop_collection()
        UsageTrackerSumServerMonthly.drop_collection()

        # generate four entries at different times
        #
        self.client.get('/')
        self.track_usage._fake_time = self.fake_time2
        self.client.get('/')
        self.track_usage._fake_time = self.fake_time3
        self.client.get('/')
        self.track_usage._fake_time = self.fake_time4
        self.client.get('/')

    def test_mongoengine_get_summary_url(self):
        """
        Test MongoEngine url summarization.
        """
        result = self.storage.get_sum(
            sumUrl,
            start_date=self.fake_hour1,
            target='http://localhost/'
        )
        # print(pprint.pprint(result))
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 2
        assert result["month"][0]['hits'] == 3

        result = self.storage.get_sum(
            "sumUrl",
            start_date=self.fake_hour4,
        )
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 1
        assert result["month"][0]['hits'] == 1

    def test_mongoengine_get_summary_remote(self):
        """
        Test MongoEngine url summarization.
        """
        result = self.storage.get_sum(
            sumRemote,
            start_date=self.fake_hour1,
            target='127.0.0.1'
        )
        # print(pprint.pprint(result))
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 2
        assert result["month"][0]['hits'] == 3

        result = self.storage.get_sum(
            "sumRemote",
            start_date=self.fake_hour4,
        )
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 1
        assert result["month"][0]['hits'] == 1

    def test_mongoengine_get_summary_useragent(self):
        """
        Test MongoEngine url summarization.
        """
        result = self.storage.get_sum(
            sumUserAgent,
            start_date=self.fake_hour1
        )
        # print(pprint.pprint(result))
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 2
        assert result["month"][0]['hits'] == 3

        result = self.storage.get_sum(
            "sumUserAgent",
            start_date=self.fake_hour4,
        )
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 1
        assert result["month"][0]['hits'] == 1

    def test_mongoengine_get_summary_language(self):
        """
        Test MongoEngine url summarization.
        """
        result = self.storage.get_sum(
            sumLanguage,
            start_date=self.fake_hour1,
            target="none"
        )
        # print(pprint.pprint(result))
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 2
        assert result["month"][0]['hits'] == 3

        result = self.storage.get_sum(
            "sumLanguage",
            start_date=self.fake_hour4,
        )
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 1
        assert result["month"][0]['hits'] == 1

    def test_mongoengine_get_summary_server(self):
        """
        Test MongoEngine url summarization.
        """
        result = self.storage.get_sum(
            sumServer,
            start_date=self.fake_hour1,
            target=self.app.name
        )
        # print(pprint.pprint(result))
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 2
        assert result["month"][0]['hits'] == 3

        result = self.storage.get_sum(
            "sumServer",
            start_date=self.fake_hour4,
        )
        assert len(result["hour"]) == 1
        assert len(result["day"]) == 1
        assert len(result["month"]) == 1
        assert result["hour"][0]['hits'] == 1
        assert result["day"][0]['hits'] == 1
        assert result["month"][0]['hits'] == 1
