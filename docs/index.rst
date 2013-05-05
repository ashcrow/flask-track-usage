Flask-Track-Usage
==================

.. module:: flask_track_usage

Basic metrics tracking for your `Flask`_ application. This focuses more on ip addresses/locations rather than tracking specific users pathing through an application. No extra cookies or javascript is used for usage tracking.

* Simple. It's a Flask extension.
* Supports either include or exempt for views.
* Provides lite abstraction for data retrieval.
* Optional `freegeoip.net <http://freegeoip.net/>`_ integration.

.. _Flask: http://flask.pocoo.org/


Installation
------------

Requirements
~~~~~~~~~~~~
* Flask: http://flask.pocoo.org/
* A storage object to save the metrics data with

Via pip
~~~~~~~
::

   $ pip install Flask-Track-Usage


Via source
~~~~~~~~~~
::

   $ python setup.py install

Usage
-----

::

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


Configuration
-------------

TRACK_USAGE_USE_FREEGEOIP
~~~~~~~~~~~~~~~~~~~~~~~~~
**Values**: True, False

**Default**: False

Turn FreeGeoIP integration on or off

TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Values**: include, exclude

**Default**: exclude

If views should be included or excluded by default

Storage
-------
The following are built in, ready to use storage backends.

.. note:: Inputs for set_up should be passed in __init__ when creating a storage instance

printer.PrintStorage
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_track_usage.storage.printer.PrintStorage


mongo.MongoPiggybackStorage
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_track_usage.storage.mongo.MongoPiggybackStorage
    :members:


mongo.MongoStorage
~~~~~~~~~~~~~~~~~~
.. autoclass:: flask_track_usage.storage.mongo.MongoStorage
    :members:


Retrieving Data
---------------
All storage backends, other than printer.PrintStorage, provide get_usage.

.. autoclass:: flask_track_usage.storage.Storage
    :members: get_usage
