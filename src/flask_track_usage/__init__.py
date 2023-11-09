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
Basic metrics tracking with Flask.
"""

import datetime
import json
import time
from six.moves.urllib_parse import quote_plus
from six.moves.urllib.request import urlopen

import six

# from flask import _request_ctx_stack, g   # _request_ctx_stack is removed since flask-3.0.0
from flask import g
from flask.globals import request_ctx
try:
    from flask_login import current_user
except Exception:
    pass

__version__ = '2.0.0'
__author__ = 'Steve Milner'
__license__ = 'MBSD'


class TrackUsage(object):
    """
    Tracks basic usage of Flask applications.
    """

    def __init__(self, app=None, storage=None, _fake_time=None):
        """
        Create the instance.

        :Parameters:
           - `app`: Optional app to use.
           - `storage`: If app is set, required list of storage callables.
        """
        #
        # `_fake_time` is to force the time stamp of the request for testing
        # purposes. It is not normally used by end users. Must be a native
        # datetime object.
        #
        self._exclude_views = set()
        self._include_views = set()

        if callable(storage):
            storage = [storage]

        self._fake_time = _fake_time

        if app is not None and storage is not None:
            self.init_app(app, storage)

    def init_app(self, app, storage):
        """
        Initialize the instance with the app.

        :Parameters:
           - `app`: Application to work with.
           - `storage`: The storage callable which will store result.
        """
        self.app = app
        self._storages = storage
        self._use_freegeoip = app.config.get(
            'TRACK_USAGE_USE_FREEGEOIP', False)
        self._freegeoip_endpoint = app.config.get(
            'TRACK_USAGE_FREEGEOIP_ENDPOINT',
            "http://extreme-ip-lookup.com/json/{ip}"
        )
        self._type = app.config.get(
            'TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS', 'exclude')

        if self._type not in ('include', 'exclude'):
            raise NotImplementedError(
                'You must set include or exclude type.')
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        """
        Done before every request that is in scope.
        """
        # ctx = _request_ctx_stack.top
        ctx = request_ctx
        view_func = self.app.view_functions.get(ctx.request.endpoint)
        if self._type == 'exclude':
            if view_func in self._exclude_views:
                return
        elif self._type == 'include':
            if view_func not in self._include_views:
                return
        else:
            raise NotImplementedError(
                'You must set include or exclude type.')
        g.start_time = datetime.datetime.utcnow()
        if not hasattr(g, "track_var"):
            g.track_var = {}

    def after_request(self, response):
        """
        The heavy lifter. This method collects the majority of data
        and passes it off for storage.

        :Parameters:
           - `response`: The response on it's way to the client.
        """
        # ctx = _request_ctx_stack.top
        ctx = request_ctx
        view_func = self.app.view_functions.get(ctx.request.endpoint)
        if self._type == 'exclude':
            if view_func in self._exclude_views:
                return response
        elif self._type == 'include':
            if view_func not in self._include_views:
                return response
        else:
            raise NotImplementedError(
                'You must set include or exclude type.')

        now = datetime.datetime.utcnow()
        speed = None
        try:
            speed = (now - g.start_time).total_seconds()
        except:
            # Older python versions don't have total_seconds()
            speed_result = (now - g.start_time)
            speed = float("%s.%s" % (
                speed_result.seconds, speed_result.microseconds))

        if self._fake_time:
            current_time = self._fake_time
        else:
            current_time = now

        data = {
            'url': ctx.request.url,
            'user_agent': ctx.request.user_agent,
            'server_name': ctx.app.name,
            'blueprint': ctx.request.blueprint,
            'view_args': ctx.request.view_args,
            'status': response.status_code,
            'remote_addr': ctx.request.remote_addr,
            'xforwardedfor': ctx.request.headers.get(
                'X-Forwarded-For', None),
            'authorization': bool(ctx.request.authorization),
            'ip_info': None,
            'path': ctx.request.path,
            'speed': float(speed),
            'date': int(time.mktime(current_time.timetuple())),
            'content_length': response.content_length,
            'request': "{} {} {}".format(
                ctx.request.method,
                ctx.request.url,
                ctx.request.environ.get('SERVER_PROTOCOL')
            ),
            'url_args': dict(
                [(k, ctx.request.args[k]) for k in ctx.request.args]
            ),
            'username': None,
            'track_var': g.track_var
        }
        if ctx.request.authorization:
            data['username'] = str(ctx.request.authorization.username)
        elif getattr(self.app, 'login_manager', None) and current_user and not current_user.is_anonymous:
            data['username'] = str(current_user)
        if self._use_freegeoip:
            clean_ip = quote_plus(str(ctx.request.remote_addr))
            if '{ip}' in self._freegeoip_endpoint:
                url = self._freegeoip_endpoint.format(ip=clean_ip)
            else:
                url = self._freegeoip_endpoint + clean_ip
            # seperate capture and conversion to aid in debugging
            text = urlopen(url).read()
            ip_info = json.loads(text)
            if url.startswith("http://extreme-ip-lookup.com/"):
                del ip_info["businessWebsite"]
                del ip_info["status"]
            data['ip_info'] = ip_info

        for storage in self._storages:
            storage(data)
        return response

    def exclude(self, view):
        """
        Excludes a view from tracking if we are in exclude mode.

        :Parameters:
           - `view`: The view to exclude.
        """
        self._exclude_views.add(view)

    def include(self, view):
        """
        Includes a view from tracking if we are in include mode.

        :Parameters:
           - `view`: The view to include.
        """
        self._include_views.add(view)

    def _modify_blueprint(self, blueprint, include_type):
        """
        Modifies a blueprint to include or exclude views.

        :Parameters:
           - `blueprint`: Blueprint instance to include.
           - `include_type`: include or exlude.
        """
        blueprint.before_request = self.before_request
        blueprint.after_request = self.after_request

        # Hack to grab views from blueprints since view_functions
        # is always empty
        class DeferredViewGrabber(object):
            views = []

            def add_url_rule(self, rule, endpoint, view_func, **options):
                self.views.append(view_func)

        dvg = DeferredViewGrabber()
        [defered(dvg) for defered in blueprint.deferred_functions]

        for view in dvg.views:
            if include_type.lower() == 'include':
                self._include_views.add(view)
            elif include_type.lower() == 'exclude':
                self._exclude_views.add(view)
            else:
                raise NotImplementedError(
                    'You must set include or exclude type for the blueprint.')
        return blueprint

    def include_blueprint(self, blueprint):
        """
        Includes an entire blueprint.

        :Parameters:
           - `blueprint`: Blueprint instance to include.
        """
        self._modify_blueprint(blueprint, 'include')

    def exclude_blueprint(self, blueprint):
        """
        Excludes an entire blueprint.

        :Parameters:
           - `blueprint`: Blueprint instance to exclude.
        """
        self._modify_blueprint(blueprint, 'exclude')


if __name__ == '__main__':
    # Example
    from flask import Flask
    app = Flask(__name__)

    # Set the configuration items manually for the example
    app.config['TRACK_USAGE_USE_FREEGEOIP'] = False
    app.config['TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'include'

    # We will just print out the data for the example
    from flask_track_usage.storage.printer import PrintWriter
    from flask_track_usage.storage.output import OutputWriter

    # Make an instance of the extension and put two writers
    t = TrackUsage(app, [PrintWriter(), OutputWriter(
        transform=lambda s: "OUTPUT: " + str(s))])

    # Include the view in the metrics
    @t.include
    @app.route('/')
    def index():
        return "Hello"

    # Run the application!
    app.run(debug=True)
