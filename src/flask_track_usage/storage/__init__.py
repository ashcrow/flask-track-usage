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
Simple storage callables package.
"""


class Storage(object):
    """
    Subclass for a more intellegent storage callable.
    """

    def __init__(self, *args, **kwargs):
        """
        Creates the instance and calls set_up.

        :Parameters:
           - `args`: All non-keyword arguments.
           - `kwargs`: All keyword arguments.
        """
        self.set_up(*args, **kwargs)

    def set_up(self, *args, **kwargs):
        """
        Sets up the created instance. Should be overridden.

        :Parameters:
           - `args`: All non-keyword arguments.
           - `kwargs`: All keyword arguments.
        """
        pass

    def store(self, data):
        """
        Executed on "function call". Must be overridden.

        :Parameters:
           - `data`: Data to store.
        """
        raise NotImplementedError('store must be implemented.')

    def __call__(self, data):
        """
        Maps function call to store.

        :Parameters:
           - `data`: Data to store.
        """
        return self.store(data)

    def _get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        """
        Implements simple usage information by criteria in a standard list form

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page
        """
        raise NotImplementedError('get_usage must be implemented.')

    def get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        """
        Returns simple usage information by criteria in a standard list form.

        .. note::
           *limit* is the amount if items returned per *page*.
           If *page* is not incremented you will always receive the
           first *limit* amount of results.

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page

        .. versionadded:: 1.0.0
           The *page* parameter.
        """
        raw_data = self._get_usage(start_date, end_date, limit, page)
        if type(raw_data) != list:
            raise Exception(
                'Container returned from _get_usage '
                'does not conform to the spec.')
        for item in raw_data:
            if type(item) != dict:
                raise Exception(
                    'An item returned from _get_usage '
                    'does not conform to the spec.')
        return raw_data
