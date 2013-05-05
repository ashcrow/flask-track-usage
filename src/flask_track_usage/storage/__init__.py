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

    def get_usage(self, start_date=None, end_date=None, limit=None):
        """
        Returns simple usage information by criteria in a standard list form.

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
        """
        raise NotImplementedError('get_usage must be implemented.')
