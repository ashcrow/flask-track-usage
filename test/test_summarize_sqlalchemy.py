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
Tests sql based summarization.
"""

import datetime
import unittest


try:
    import sqlalchemy as sql
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False



# from flask_track_usage import TrackUsage
# # from flask_track_usage.storage.mongo import MongoEngineStorage
# from flask_track_usage.summarization import (
#     sumUrl,
#     sumRemote,
#     sumUserAgent,
#     sumLanguage,
#     sumServer,
# )

# # if HAS_MONGOENGINE:
# #     from flask_track_usage.summarization.postgresqlstorage import (
# #         UsageTrackerSumUrlHourly,
# #         UsageTrackerSumUrlDaily,
# #         UsageTrackerSumUrlMonthly,
# #         UsageTrackerSumRemoteHourly,
# #         UsageTrackerSumRemoteDaily,
# #         UsageTrackerSumRemoteMonthly,
# #         UsageTrackerSumUserAgentHourly,
# #         UsageTrackerSumUserAgentDaily,
# #         UsageTrackerSumUserAgentMonthly,
# #         UsageTrackerSumLanguageHourly,
# #         UsageTrackerSumLanguageDaily,
# #         UsageTrackerSumLanguageMonthly,
# #         UsageTrackerSumServerHourly,
# #         UsageTrackerSumServerDaily,
# #         UsageTrackerSumServerMonthly,
# #     )

# from . import FlaskTrackUsageTestCase


# @unittest.skipUnless(HAS_MONGOENGINE, "Requires MongoEngine")
# class TestMongoEngineSummarizeBasic(FlaskTrackUsageTestCase):
#     """
#     Tests MongoEngine summaries.
#     """

#     def setUp(self):
#         """
#         Set up an app to test with.
#         """
#         FlaskTrackUsageTestCase.setUp(self)
#         self.storage = MongoEngineStorage(hooks=[
#             sumUrl,
#             sumRemote,
#             sumUserAgent,
#             sumLanguage,
#             sumServer
#         ])
#         self.track_usage = TrackUsage(self.app, self.storage)
#         # Clean out the summary
#         UsageTrackerSumUrlHourly.drop_collection()
#         UsageTrackerSumUrlDaily.drop_collection()
#         UsageTrackerSumUrlMonthly.drop_collection()
#         UsageTrackerSumRemoteHourly.drop_collection()
#         UsageTrackerSumRemoteDaily.drop_collection()
#         UsageTrackerSumRemoteMonthly.drop_collection()
#         UsageTrackerSumUserAgentHourly.drop_collection()
#         UsageTrackerSumUserAgentDaily.drop_collection()
#         UsageTrackerSumUserAgentMonthly.drop_collection()
#         UsageTrackerSumLanguageHourly.drop_collection()
#         UsageTrackerSumLanguageDaily.drop_collection()
#         UsageTrackerSumLanguageMonthly.drop_collection()
#         UsageTrackerSumServerHourly.drop_collection()
#         UsageTrackerSumServerDaily.drop_collection()
#         UsageTrackerSumServerMonthly.drop_collection()
#         # trigger one timed summary
#         self.now = datetime.datetime.utcnow()
#         self.hour = self.now.replace(minute=0, second=0, microsecond=0)
#         self.day = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
#         self.month = self.now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         self.client.get('/')

#     def test_postgresql_url_summary(self):
#         """
#         Test MongoEngine url summarization.
#         """
#         hour_doc = UsageTrackerSumUrlHourly.objects.first()
#         assert hour_doc.url == 'http://localhost/'
#         assert hour_doc.date == self.hour
#         assert hour_doc.hits == 1
#         assert hour_doc.transfer > 1
#         day_doc = UsageTrackerSumUrlDaily.objects.first()
#         assert day_doc.url == 'http://localhost/'
#         assert day_doc.date == self.day
#         assert day_doc.hits == 1
#         assert day_doc.transfer > 1
#         month_doc = UsageTrackerSumUrlMonthly.objects.first()
#         assert month_doc.url == 'http://localhost/'
#         assert month_doc.date == self.month
#         assert month_doc.hits == 1
#         assert month_doc.transfer > 1

    # def test_postgresql_remote_summary(self):
    #     """
    #     Test MongoEngine remote IP summarization.
    #     """
    #     hour_doc = UsageTrackerSumRemoteHourly.objects.first()
    #     assert hour_doc.remote_addr == '127.0.0.1'
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumRemoteDaily.objects.first()
    #     assert day_doc.remote_addr == '127.0.0.1'
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumRemoteMonthly.objects.first()
    #     assert month_doc.remote_addr == '127.0.0.1'
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

    # def test_postgresql_user_agent_summary(self):
    #     """
    #     Test MongoEngine User Agent summarization.
    #     """
    #     hour_doc = UsageTrackerSumUserAgentHourly.objects.first()
    #     assert hour_doc.user_agent_string.startswith("werkzeug/")
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumUserAgentDaily.objects.first()
    #     assert day_doc.user_agent_string.startswith("werkzeug/")
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumUserAgentMonthly.objects.first()
    #     assert month_doc.user_agent_string.startswith("werkzeug/")
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

    # def test_postgresql_language_summary(self):
    #     """
    #     Test MongoEngine Language summarization.
    #     """
    #     hour_doc = UsageTrackerSumLanguageHourly.objects.first()
    #     assert hour_doc.language == 'none'
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumLanguageDaily.objects.first()
    #     assert day_doc.language == 'none'
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumLanguageMonthly.objects.first()
    #     assert month_doc.language == 'none'
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

    # def test_postgresql_server_summary(self):
    #     """
    #     Test MongoEngine server summarization.
    #     """
    #     hour_doc = UsageTrackerSumServerHourly.objects.first()
    #     assert hour_doc.date == self.hour
    #     assert hour_doc.hits == 1
    #     assert hour_doc.transfer > 1
    #     day_doc = UsageTrackerSumServerDaily.objects.first()
    #     assert day_doc.date == self.day
    #     assert day_doc.hits == 1
    #     assert day_doc.transfer > 1
    #     month_doc = UsageTrackerSumServerMonthly.objects.first()
    #     assert month_doc.date == self.month
    #     assert month_doc.hits == 1
    #     assert month_doc.transfer > 1

