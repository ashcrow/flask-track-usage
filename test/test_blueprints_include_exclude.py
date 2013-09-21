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

from flask import Blueprint
from flask_track_usage import TrackUsage

from . import FlaskTrackUsageTestCase, TestStorage


class TestBlueprintIncludeExclude(FlaskTrackUsageTestCase):
    """
    Tests blueprint include/exclude functionality.
    """

    def setUp(self):
        """
        Set up an app to test with.
        """
        FlaskTrackUsageTestCase.setUp(self)
        self.storage = TestStorage()
        self.blueprint = Blueprint('test_blueprint', __name__)

        @self.blueprint.route('/included')
        def included():
            return "INCLUDED"

        @self.blueprint.route('/excluded')
        def excluded():
            return "EXCLUDED"

        self.app.register_blueprint(self.blueprint)

    def test_raw_blueprint(self):
        """
        Verify that raw blueprints don't get modified.
        """
        self.app.config[
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'include'
        tu = TrackUsage(self.app, self.storage)

        # There should be no included/excluded views
        assert len(tu._include_views) == 0
        assert len(tu._exclude_views) == 0

        # There should be no storing of data at all
        for page in ('/', '/included', '/excluded'):
            self.client.get(page)
            with self.assertRaises(IndexError):
                self.storage.get()

    def test_include_blueprint(self):
        """
        Verify that an entire blueprint can be included.
        """
        self.app.config[
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'include'
        tu = TrackUsage(self.app, self.storage)
        tu.include_blueprint(self.blueprint)

        # There should be 2 included views, no excluded views
        assert len(tu._include_views) == 2
        assert len(tu._exclude_views) == 0

        # Both paged should store
        for page in ('/included', '/excluded'):
            self.client.get(page)
            assert type(self.storage.get()) is dict

        # But the index (outside of the blueprint) should not
        self.client.get('/')
        with self.assertRaises(IndexError):
            self.storage.get()

    def test_exclude_blueprint(self):
        """
        Verify that an entire blueprint can be excluded.
        """
        self.app.config[
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'exclude'
        tu = TrackUsage(self.app, self.storage)
        tu.exclude_blueprint(self.blueprint)

        # There should be 2 excluded views, 0 included views
        assert len(tu._include_views) == 0
        assert len(tu._exclude_views) == 2

        # Index should store something
        self.client.get('/')
        assert type(self.storage.get()) is dict

        # Both pages should not store anything
        for page in ('/included', '/excluded'):
            self.client.get(page)
            with self.assertRaises(IndexError):
                self.storage.get()
