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
Test include/exclude functionality.
"""

from flask_track_usage import TrackUsage

from . import FlaskTrackUsageTestCase, TestStorage


class TestIncludeExclude(FlaskTrackUsageTestCase):
    """
    Tests include/exclude functionality.
    """

    def setUp(self):
        """
        Set up an app to test with.
        """
        FlaskTrackUsageTestCase.setUp(self)
        self.storage = TestStorage()

    def test_neither_include_nor_exclude(self):
        """
        Verify that we fail when we don't state include or exclude.
        """
        self.app.config[
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = ''
        with self.assertRaises(NotImplementedError):
            TrackUsage(self.app, self.storage)

    def test_late_neither_include_nor_exclude(self):
        """
        Make sure that if someone attempts to change the type to something
        unsupported we fail
        """
        self.app.config[
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'include'
        self.track_usage = TrackUsage(self.app, self.storage)
        self.track_usage._type = ''
        with self.assertRaises(NotImplementedError):
            self.client.get('/')

    def test_include_type(self):
        """
        Test that include only covers what is included.
        """
        self.app.config[
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'include'
        self.track_usage = TrackUsage(self.app, self.storage)

        @self.track_usage.include
        @self.app.route('/included')
        def included():
            return "INCLUDED"

        # /includeds hould give results
        self.client.get('/included')
        assert type(self.storage.get()) is dict
        # / should not give results as it is not included
        self.client.get('/')
        with self.assertRaises(IndexError):
            self.storage.get()

    def test_exclude_type(self):
        """
        Test that exclude covers anything not excluded.
        """
        self.app.config[
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'exclude'
        self.track_usage = TrackUsage(self.app, self.storage)

        @self.track_usage.exclude
        @self.app.route('/excluded')
        def excluded():
            return "INCLUDED"

        # / hould give results
        self.client.get('/')
        assert type(self.storage.get()) is dict
        # /excluded should not give results as it is excluded
        self.client.get('/excluded')
        with self.assertRaises(IndexError):
            self.storage.get()
