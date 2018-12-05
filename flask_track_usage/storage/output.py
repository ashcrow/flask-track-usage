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
Output writer.
"""

from flask_track_usage.storage import Writer


class OutputWriter(Writer):
    """
    Writes data to a provided file like object.
    """

    def set_up(self, output=None, transform=None):
        """
        Sets the file like object.

        .. note::

           Make sure to pass in instances which allow multiple writes.

        :Parameters:
           - `output`: A file like object to use. Default: sys.stderr
           - `transform`: Optional function to modify the output before write.
        """
        self.transform = transform
        if self.transform is None:
            self.transform = str

        if output is None:
            import sys
            output = sys.stderr

        if not hasattr(output, 'write'):
            raise TypeError('A file like object must have a write method')
        elif not hasattr(output, 'writable'):
            raise TypeError('A file like object must have a writable method')
        elif not output.writable():
            raise ValueError('Provided file like object is not writable')

        self.flushable = False
        if hasattr(output, 'flush'):
            self.flushable = True

        self.output = output

    def store(self, data):
        """
        Executed on "function call".

        :Parameters:
           - `data`: Data to store.
        """
        self.output.write(self.transform(data))
        if self.flushable:
            self.output.flush()
