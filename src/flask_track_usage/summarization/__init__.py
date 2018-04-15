import mongoenginestorage
import sqlstorage

"""
Summarization routines.

This file contains the generic summary functions. They are, essentially, stubs
that search for the correct storage support based on the class information
passed.
"""


def _set_up(sum_name, **kwargs):
    method_name = "{}_set_up".format(sum_name)
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
        # not having *_set_up is fine: gracefully return
        return
    method(**kwargs)



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


class sumUrl(object):

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumUrl", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumUrl", **kwargs)


class sumRemote(object):
    """
    Traffic is summarized for each remote IP address seen by the Flask server.
    """
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumRemote", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumRemote", **kwargs)


class sumUserAgent(object):
    """
    Traffic is summarized for each client (aka web browser) seen by the Flask
    server.
    """
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumUserAgent", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumUserAgent", **kwargs)


class sumLanguage(object):
    """
    Traffic is summarized for each language seen in the requests sent to the
    Flask server.
    """
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumLanguage", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumLanguage", **kwargs)


class sumServer(object):
    """
    Traffic is summarized for all requests sent to the Flask server. This
    metric is mostly useful for diagnosing performance.
    """
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumServer", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumServer", **kwargs)


# TBD
class sumVisitor(object):
    """
    Traffic is summarized for each unique visitor of the Flask server. For this
    to function, the optional TRACK_USAGE_COOKIE function must be enabled in
    config.

    This metric is limited by the cookie technology. User behavior such as
    switching browsers or turning on "anonymous mode" on a browser will make
    them appear to be multiple users.
    """
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumVisitor", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumVisitor", **kwargs)


#TBD
class sumGeo(object):
    """
    Traffic is summarized for the tracked geographies of remote IPs seen by the
    Flask server. For this to properly function, the optional
    TRACK_USAGE_FREEGEOIP config must be enabled. While the geography function
    provides a great deal of information, only the country is used for this
    summarization.
    """
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumGeo", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumGeo", **kwargs)


class sumBasic(object):
    """
    A shortcut that, in turn, calls sumUrl, sumRemote, sumUserAgent,
    sumLanguage, and sumServer
    """
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        _set_up("sumUrl", **kwargs)
        _set_up("sumRemote", **kwargs)
        _set_up("sumUserAgent", **kwargs)
        _set_up("sumLanguage", **kwargs)
        _set_up("sumServer", **kwargs)
        return

    def __call__(self, **kwargs):
        _caller("sumUrl", **kwargs)
        _caller("sumRemote", **kwargs)
        _caller("sumUserAgent", **kwargs)
        _caller("sumLanguage", **kwargs)
        _caller("sumServer", **kwargs)
