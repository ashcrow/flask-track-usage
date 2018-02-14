import mongoenginestorage

"""
Summarization routines.

This file contains the generic summary functions. They are, essentially, stubs
that search for the correct storage support based on the class information
passed.
"""


def _caller(method_name, **kwargs):
    if "_parent_class_name" not in kwargs:
        raise NotImplementedError(
            "{} can only be used as a Storage class hook.".format(method_name)
        )
    try:
        lib_name = kwargs["_parent_class_name"].lower()
        library = globals()[lib_name]
    except KeyError:
        raise ImportError(
            "the {} class does not currently support"
            " summarization.".format(kwargs["_parent_class_name"])
        )
    try:
        method = getattr(library, method_name)
    except AttributeError:
        raise NotImplementedError(
            '{} not implemented for this Storage class.'.format(method_name)
        )
    method(**kwargs)


def sumUrl(**kwargs):
    """
    Traffic is summarized for each URL requested of the Flask server.
    """
    _caller("sumUrl", **kwargs)


def sumRemote(**kwargs):
    """
    Traffic is summarized for each remote IP address seen by the Flask server.
    """
    _caller("sumRemote", **kwargs)


def sumUserAgent(**kwargs):
    """
    Traffic is summarized for each client (aka web browser) seen by the Flask
    server.
    """
    _caller("sumUserAgent", **kwargs)


def sumLanguage(**kwargs):
    """
    Traffic is summarized for each language seen in the requests sent to the
    Flask server.
    """
    _caller("sumLanguage", **kwargs)


def sumServer(**kwargs):
    """
    Traffic is summarized for all requests sent to the Flask server. This
    metric is mostly useful for diagnosing performance.
    """
    _caller("sumServer", **kwargs)


def sumVisitor(**kwargs):
    """
    Traffic is summarized for each unique visitor of the Flask server. For this
    to function, the optional TRACK_USAGE_COOKIE function must be enabled in
    config.

    This metric is limited by the cookie technology. User behavior such as
    switching browsers or turning on "anonymous mode" on a browser will make
    them appear to be multiple users.
    """
    _caller("sumVisitor", **kwargs)


def sumGeo(**kwargs):
    """
    Traffic is summarized for the tracked geographies of remote IPs seen by the
    Flask server. For this to properly function, the optional
    TRACK_USAGE_FREEGEOIP config must be enabled. While the geography function
    provides a great deal of information, only the country is used for this
    summarization.
    """
    _caller("sumGeo", **kwargs)


def sumBasic(**kwargs):
    """
    A shortcut that, in turn, calls sumUrls, sumRemotes, sumUserAgents,
    sumLanguages, and sumServer
    """
    sumUrl(**kwargs)
    sumRemote(**kwargs)
    sumUserAgent(**kwargs)
    sumLanguage(**kwargs)
    sumServer(**kwargs)
