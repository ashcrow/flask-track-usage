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
Basic data tests.
"""

import datetime

from flask_track_usage import TrackUsage

from . import FlaskTrackUsageTestCase, TestStorage


class TestData(FlaskTrackUsageTestCase):
    """
    Tests specific to expected data.
    """

    def setUp(self):
        """
        Set up an app to test with.
        """
        FlaskTrackUsageTestCase.setUp(self)
        self.storage = TestStorage()
        self.track_usage = TrackUsage(self.app, self.storage)

    def test_expected_data(self):
        """
        Test that the data is in the expected formart.
        """
        self.client.get('/')
        result = self.storage.get()
        self.assertEquals(result.__class__, dict)
        self.assertIsNone(result['blueprint'])
        self.assertIsNone(result['ip_info'])
        self.assertEquals(result['status'], 200)
        self.assertEquals(result['remote_addr'], '127.0.0.1')
        self.assertEquals(result['speed'].__class__, float)
        self.assertEquals(result['view_args'], {})
        self.assertEquals(result['url'], 'http://localhost/')
        self.assertEquals(result['path'], '/')
        self.assertEquals(result['authorization'], False)
        self.assertTrue(result['user_agent'].string.startswith('werkzeug'))
        self.assertEquals(type(result['date']), int)
        self.assertTrue(datetime.datetime.fromtimestamp(result['date']))
