# Copyright (c) 2014 Gouthaman Balaraman
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
SQL storage based on SQLAlchemy
"""

from . import Storage
import json
import datetime


class SQLStorage(Storage):
    """
    Uses SQLAlchemy to connect to various databases such as SQLite, Oracle,
    MySQL, Postgres, etc. Please SQLAlchemy wrapper for full support and
    functionalities.

    .. versionadded:: 1.0.0
       SQLStorage was added.
    .. versionchanged:: 1.1.0
       Initialization no longer accepts a connection string.
    .. versionchanged:: 1.1.0
       A SQLAlchemy engine instance can optionally be passed in.
    .. versionchanged:: 1.1.0
       A SQLAlchemy metadata instance can optionally be passed in.
    """

    def set_up(self, engine=None, metadata=None, table_name="flask_usage",
               db=None):
        """
        Sets the SQLAlchemy database. There are two ways to initialize the
        SQLStorage: 1) by passing the SQLAlchemy `engine` and `metadata`
        instances or 2) by passing the Flask-SQLAlchemy's `SQLAlchemy`
        object `db`.

        :Parameters:
           - `engine`: The SQLAlchemy engine object
           - `metadata`: The SQLAlchemy MetaData object
           - `table_name`: Table name for storing the analytics. Defaults to \
                           `flask_usage`.
           - `db`: Instead of providing the engine, one can optionally
                   provide the Flask-SQLAlchemy's SQLALchemy object created as
                   SQLAlchemy(app).

        .. versionchanged:: 1.1.0
           xforwardfor column added directly after remote_addr
        """

        import sqlalchemy as sql
        if db:
            self._eng = db.engine
            self._metadata = db.metadata
        else:
            if engine is None:
                raise ValueError("Both db and engine args cannot be None")
            self._eng = engine
            self._metadata = metadata or sql.MetaData()
        self._con = None
        with self._eng.begin() as self._con:
            if not self._con.dialect.has_table(self._con, table_name):
                self.track_table = sql.Table(
                    table_name, self._metadata,
                    sql.Column('id', sql.Integer, primary_key=True),
                    sql.Column('url', sql.String(128)),
                    sql.Column('ua_browser', sql.String(16)),
                    sql.Column('ua_language', sql.String(16)),
                    sql.Column('ua_platform', sql.String(16)),
                    sql.Column('ua_version', sql.String(16)),
                    sql.Column('blueprint', sql.String(16)),
                    sql.Column('view_args', sql.String(64)),
                    sql.Column('status', sql.Integer),
                    sql.Column('remote_addr', sql.String(24)),
                    sql.Column('xforwardedfor', sql.String(24)),
                    sql.Column('authorization', sql.Boolean),
                    sql.Column('ip_info', sql.String(128)),
                    sql.Column('path', sql.String(32)),
                    sql.Column('speed', sql.Float),
                    sql.Column('datetime', sql.DateTime)
                )
            else:
                self._metadata.reflect(bind=self._eng)
                self.track_table = self._metadata.tables[table_name]

    def store(self, data):
        """
        Executed on "function call".

        :Parameters:
           - `data`: Data to store.

        .. versionchanged:: 1.1.0
           xforwardfor column added directly after remote_addr
        """
        user_agent = data["user_agent"]
        utcdatetime = datetime.datetime.fromtimestamp(data['date'])
        if data["ip_info"]:
            t = {}
            for key in data["ip_info"]:
                t[key] = data["ip_info"][key]
                if len(json.dumps(t)) > 128:
                    del t[key]
                    break
            ip_info_str = json.dumps(t)
        else:
            ip_info_str = None
        with self._eng.begin() as con:
            stmt = self.track_table.insert().values(
                url=data['url'],
                ua_browser=user_agent.browser,
                ua_language=user_agent.language,
                ua_platform=user_agent.platform,
                ua_version=user_agent.version,
                blueprint=data["blueprint"],
                view_args=json.dumps(
                    data["view_args"], ensure_ascii=False
                )[:64],
                status=data["status"],
                remote_addr=data["remote_addr"],
                xforwardedfor=data["xforwardedfor"],
                authorization=data["authorization"],
                ip_info=ip_info_str,
                path=data["path"],
                speed=data["speed"],
                datetime=utcdatetime
            )
            con.execute(stmt)

    def _get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        """
        This is what translates the raw data into the proper structure.

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page

        .. versionchanged:: 1.1.0
           xforwardfor column added directly after remote_addr
        """
        raw_data = self._get_raw(start_date, end_date, limit, page)
        usage_data = [
            {
                'url': r[1],
                'user_agent': {
                    'browser': r[2],
                    'language': r[3],
                    'platform': r[4],
                    'version': r[5],
                },
                'blueprint': r[6],
                'view_args': r[7] if r[7] != '{}' else None,
                'status': int(r[8]),
                'remote_addr': r[9],
                'xforwardedfor': r[10],
                'authorization': r[11],
                'ip_info': r[12],
                'path': r[13],
                'speed': r[14],
                'date': r[15]
            } for r in raw_data]
        return usage_data

    def _get_raw(self, start_date=None, end_date=None, limit=500, page=1):
        """
        This is the raw getter from database

        :Parameters:
           - `start_date`: datetime.datetime representation of starting date
           - `end_date`: datetime.datetime representation of ending date
           - `limit`: The max amount of results to return
           - `page`: Result page number limited by `limit` number in a page

        .. versionchanged:: 1.1.0
           xforwardfor column added directly after remote_addr
        """
        import sqlalchemy as sql
        page = max(1, page)   # min bound
        if end_date is None:
            end_date = datetime.datetime.utcnow()
        if start_date is None:
            start_date = datetime.datetime(1970, 1, 1)
        with self._eng.begin() as con:
            _table = self.track_table
            stmt = sql.select([self.track_table])\
                .where(_table.c.datetime.between(start_date, end_date))\
                .limit(limit)\
                .offset(limit * (page - 1))\
                .order_by(sql.desc(self.track_table.c.datetime))
            res = con.execute(stmt)
            result = res.fetchall()
        return result
