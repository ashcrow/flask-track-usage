Flask-Track-Usage Hooks
=======================

The library supports post-storage functions that can optionally do more after the request itself is stored.

How To Use
----------

To use, simply add the list of functions you wish to call from the context of call to TrackUsage.

For example, to add sumRemotes and sumLanguages to a MongoEngineStorage storage:

.. code-block:: python

    from flask.ext.track_usage import TrackUsage
    from flask.ext.track_usage.storage.mongo import MongoEngineStorage
    from flask.ext.track_usage.summarization import sumRemotes, sumLanguages

    t = TrackUsage(app, [MongoEngineStorage(hooks=[sumRemotes, sumLanguages])])

Standard Summary Hooks
----------------------

Time Periods for ALL Summary Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When keeping live metrics for each of the summaries, the following time periods are used:

:Hour:
  one common unit of "storage" is kept to keep track of the hourly traffic for each hour of a particular date.

:Date:
  one common unit of "storage" is kept to keep track of the daily traffic for a particular date.

:Month:
  one common unit of "storage" is kept to keep track of the monthly traffic for a particular
  month. The month stored is the first day of the month. For example, the summary for March
  2017 would be stored under the date of 2017-03-01.

Please note that this library DOES NOT handle expiration of old data. If you wish to delete, say, hourly data that is over 60 days old, you will need to create a seperate process to handle this. This library merely adds or updates new data and presumes limitless storage.

Summary Targets for ALL Summary Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, the following two data targets are summarized for each of the Time Periods.

:Hits:
  The total number of requests seen.
:Transfer:
  The total number of bytes transfered in response to all requests seen.

sumUrls -- URLs
~~~~~~~~~~~~~~~

Traffic is summarized for each URL requested of the Flask server.

sumRemotes -- remote IPs
~~~~~~~~~~~~~~~~~~~~~~~~

Traffic is summarized for each remote IP address seen by the Flask server.

sumUserAgents -- user agent clients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Traffic is summarized for each client (aka web browser) seen by the Flask server.

sumLanugages -- languages
~~~~~~~~~~~~~~~~~~~~~~~~~

Traffic is summarized for each language seen in the requests sent to the Flask server.

sumServer -- site-wide server hits/traffic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Traffic is summarized for all requests sent to the Flask server. This metric is mostly useful for diagnosing performance.

sumVisitors -- unique visitors (as tracked by cookies)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Traffic is summarized for each unique visitor of the Flask server. For this to function, the optional TRACK_USAGE_COOKIE function must be enabled in config.

This metric is limited by the cookie technology. User behavior such as switching browsers or turning on "anonymous mode" on a browser will make them appear to be multiple users.

sumGeo -- physical country of remote IPs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Traffic is summarized for the tracked geographies of remote IPs seen by the Flask server. For this to properly function, the optional TRACK_USAGE_FREEGEOIP config must be enabled. While the geography function provides a great deal of information, only the country is used for this summarization.
