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
    """

    def set_up(self, conn_str, table_name="flask_usage"):
        """
        Sets the SQLAlchemy database

        :Parameters:
           - `conn_str`: The SQLAlchemy connection string
           - `table_name`: Table name for storing the analytics. Defaults to \
                           `flask_usage`.
        """

        import sqlalchemy as sql
        self._eng = sql.create_engine(conn_str)
        # sqlite needs conn and inserts to be issued by the same thread
        self._issqlite = self._eng.name == 'sqlite'
        self._con = self._eng.connect()
        meta = sql.MetaData()
        if not self._con.dialect.has_table(self._con, table_name):
            self.track_table = sql.Table(
                table_name, meta,
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
                sql.Column('authorization', sql.Boolean),
                sql.Column('ip_info', sql.String(128)),
                sql.Column('path', sql.String(32)),
                sql.Column('speed', sql.Float),
                sql.Column('datetime', sql.DateTime)
            )
            meta.create_all(self._eng)
        else:
            meta.reflect(bind=self._eng)
            self.track_table = meta.tables[table_name]
        if self._issqlite:
            self._con.close()

    def store(self, data):
        """
        Executed on "function call".

        :Parameters:
           - `data`: Data to store.
        """
        user_agent = data["user_agent"]
        utcdatetime = datetime.datetime.fromtimestamp(data['date'])
        stmt = self.track_table.insert().values(
            url=data['url'],
            ua_browser=user_agent.browser,
            ua_language=user_agent.language,
            ua_platform=user_agent.platform,
            ua_version=user_agent.version,
            blueprint=data["blueprint"],
            view_args=json.dumps(data["view_args"], ensure_ascii=False),
            status=data["status"],
            remote_addr=data["remote_addr"],
            authorization=data["authorization"],
            ip_info=data["ip_info"],
            path=data["path"],
            speed=data["speed"],
            datetime=utcdatetime
        )
        con = self._eng.connect() if self._issqlite else self._con
        con.execute(stmt)
        if self._issqlite:
            con.close()

    def get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        raw_data = self._get_usage(start_date, end_date, limit, page)
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
                'view_args': r[7],  # if r[6] != '{}' else None ,
                'status': int(r[8]),
                'remote_addr': r[9],
                'authorization': r[10],
                'ip_info': r[11],
                'path': r[12],
                'speed': r[13],
                'date': r[14]
            } for r in raw_data]
        return usage_data

    def _get_usage(self, start_date=None, end_date=None, limit=500, page=1):
        '''
        This is the raw getter from database
        '''
        import sqlalchemy as sql
        page = max(1, page)   # min bound
        if end_date is None:
            end_date = datetime.datetime.utcnow()
        if start_date is None:
            start_date = datetime.datetime(1970, 1, 1)
        stmt = sql.select([self.track_table])\
            .where(self.track_table.c.datetime.between(start_date, end_date))\
            .limit(limit)\
            .offset(limit*(page-1))\
            .order_by(sql.desc(self.track_table.c.datetime))
        con = self._eng.connect() if self._issqlite else self._con
        res = con.execute(stmt)
        result = res.fetchall()
        if self._issqlite:
            con.close()
        return result
