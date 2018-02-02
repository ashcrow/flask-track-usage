Flask-Track-Usage Hooks
=======================

The library supports post-storage functions that can do extra functions after the 


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

Hour: one common unit of "storage" is kept to keep track of the hourly traffic for each hour of a particular date.

Date: one common unit of "storage" is kept to keep track of the daily traffic for a particular date.

Month: one common unit of "storage" is kept to keep track of the monthly traffic for a particular month. The month stored is the first day of the month. For example, the summary for March 2017 would be stored under the date of 2017-03-01.

Please note that this library DOES NOT handle expiration of old data. If you wish to delete, say, hourly data that is over 60 days old, you will need to create a seperate process to handle this. This library merely adds or updates new data and presumes limitless storage.

Summary Targets for ALL Summary Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, the following two data targets are summarized for each of the Time Periods.

1. Hits: the total number of requests seen.
2. Transfer: the total number of bytes transfered in response to all requests seen.

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


sumBasic -- shortcut basic 5 summaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A shortcut that, in turn, calls sumUrls, sumRemotes, sumUserAgents, sumLanguages, and sumServer.

WARNING: do not call both sumBasic and one of the five basic summaries. Doing so will likely cause duplicate counting. So, for example, don't call both "sumBasic" and "sumServer".

How to Write Your Own Hooks
---------------------------

To write your own hook....

How to Add Hooks to the Library
-------------------------------

To add to the hooks to the Flask-Track-Usage library, add the "stub" code file seen in the "summarization" directory along with the reference to in in the "__init__.py" file. See existing code for examples.

Each "stub" has the sole purpose of looking for the corresponding method in the in it's calling class. So, if you write a summary function called "sumMyNewThing" it will look for a "sumMyNewThing" method in the Storage class it is associated with.

Not every storage class supports every summary function, so it is critical that each storage class fail gracefully and simply skips any methods not found.