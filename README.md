flask-track-usage
=================

[![Build Status](https://travis-ci.org/ashcrow/flask-track-usage.png?branch=master)](https://travis-ci.org/ashcrow/flask-track-usage)

Basic metrics tracking for the Flask framework. This focuses more on ip addresses/locations rather than tracking specific users pathing through an application. No extra cookies or javascript is used for usage tracking.

Features
--------
* Simple. It's a Flask extension.
* Supports either include or exempt for views.
* Optional freegeoip.net integration.


Requirements
------------
* Flask: http://flask.pocoo.org/
* A storage object to save the metrics data with


Configuration Items
-------------------
* TRACK_USAGE_USE_FREEGEOIP
  * Boolean
  * If freegeoip.net should be used
* TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS
  * include, exclude
  * If views should be included manually or if views should be manully excluded

Basic Example
-------------
```python
# Create the Flask 'app'
from flask import Flask
app = Flask(__name__)

# Set the configuration items manually for the example
app.config['TRACK_USAGE_USE_FREEGEOIP'] = False
app.config['TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'include'

# We will just print out the data for the example
from flask.ext.track_usage import TrackUsage
from flask.ext.track_usage.storage.printer import PrintStorage

# Make an instance of the extension
t = TrackUsage(app, PrintStorage())

# Make an instance of the extension
t = TrackUsage(app, storage)

# Include the view in the metrics
@t.include
@app.route('/')
def index():
    return "Hello"

# Run the application!
app.run(debug=True)
```

Example Output From Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~
```python
{
    'blueprint': None,
    'view_args': {},
    'ip_info': None,
    'status': 200,
    'user_agent': <UserAgent 'chrome'/26.0.1410.65>,
    'remote_addr': '127.0.0.1',
    'url': 'http://127.0.0.1:5000/',
    'speed': 0.009223,
    'authorization': False,
    'path': '/',
    'date': 1366936473,
}
```

Similar Projects
----------------
* https://github.com/srounet/Flask-Analytics