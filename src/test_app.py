#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from flask import Flask
from flask_track_usage import TrackUsage
from flask_track_usage.storage.redis_db import RedisStorage
from datetime import datetime


app = Flask(__name__)
redis = RedisStorage()
track = TrackUsage(app, redis)


@app.route('/')
def index():
    return "ok"


@track.exclude
@app.route('/usage')
def usage():
    now = datetime.now()
    yesterday = datetime.fromtimestamp(1421111101)  # 2015-1-13 02:05:01
    res = redis.get_usage(now, yesterday)
    # res = redis.get_usage()
    print res
    return json.dumps(res)

app.config['PROPAGATE_EXCEPTIONS'] = True
app.run(port=8081, use_reloader=True)
