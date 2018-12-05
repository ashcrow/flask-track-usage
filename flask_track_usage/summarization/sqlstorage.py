import datetime
try:
    import sqlalchemy as sql
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

try:
    import psycopg2
    from sqlalchemy.dialects.postgresql import insert
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


def _check_environment(**kwargs):
    if not HAS_SQLALCHEMY:
        return False
    return True


def _check_postgresql(**kwargs):
    if not HAS_POSTGRES:
        return False
    if kwargs["_parent_self"]._eng.driver != 'psycopg2':
        return False
    return True


def trim_times(unix_timestamp):
    date = datetime.datetime.fromtimestamp(unix_timestamp)
    hour = date.replace(minute=0, second=0, microsecond=0)
    day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return hour, day, month


def increment(con, table, dt, data, **values):
    stmt = insert(table).values(
        date=dt,
        hits=1,
        transfer=data['content_length'],
        **values
    ).on_conflict_do_update(
        index_elements=['date'],
        set_=dict(
            hits=table.c.hits + 1,
            transfer=table.c.transfer + data['content_length']
        )
    )
    con.execute(stmt)


def create_tables(table_list, **kwargs):
    self = kwargs["_parent_self"]
    with self._eng.begin() as self._con:
        for base_sum_table_name in table_list:
            key_field, _ = base_sum_table_name.split("_")
            sum_table_name = "{}_{}".format(
                self.table_name, base_sum_table_name
            )
            if not self._con.dialect.has_table(self._con, sum_table_name):
                self.sum_tables[base_sum_table_name] = sql.Table(
                    sum_table_name,
                    self._metadata,
                    sql.Column('date', sql.DateTime, primary_key=True),
                    sql.Column(key_field, sql.String(128)),
                    sql.Column('hits', sql.Integer),
                    sql.Column('transfer', sql.Integer)
                )
            else:
                self._metadata.reflect(bind=self._eng)
                self.sum_tables[base_sum_table_name] = (
                    self._metadata.tables[sum_table_name])


######################################################
#
#   sumURL
#
######################################################

if not HAS_SQLALCHEMY:

    def sumUrl(**kwargs):
        raise NotImplementedError("SQLAlchemy library not installed")

else:

    def sumUrl_set_up(*args, **kwargs):
        tables = ["url_hourly", "url_daily", "url_monthly"]
        create_tables(tables, **kwargs)

    def sumUrl(**kwargs):
        if not _check_environment(**kwargs):
            return
        if not _check_postgresql(**kwargs):
            raise NotImplementedError("Only PostgreSQL currently supported")
            return

        hour, day, month = trim_times(kwargs['date'])
        x = kwargs["_parent_self"]
        with x._eng.begin() as con:
            increment(
                con,
                x.sum_tables["url_hourly"],
                hour,
                kwargs,
                url=kwargs['url']
            )
            increment(
                con,
                x.sum_tables["url_daily"],
                day,
                kwargs,
                url=kwargs['url']
            )
            increment(
                con,
                x.sum_tables["url_monthly"],
                month,
                kwargs,
                url=kwargs['url']
            )

        return


######################################################
#
#   sumRemote
#
######################################################

if not HAS_SQLALCHEMY:

    def sumRemote(**kwargs):
        raise NotImplementedError("SQLAlchemy library not installed")

else:

    def sumRemote_set_up(*args, **kwargs):
        tables = ["remote_hourly", "remote_daily", "remote_monthly"]
        create_tables(tables, **kwargs)

    def sumRemote(**kwargs):
        if not _check_environment(**kwargs):
            return
        if not _check_postgresql(**kwargs):
            raise NotImplementedError("Only PostgreSQL currently supported")
            return

        hour, day, month = trim_times(kwargs['date'])
        x = kwargs["_parent_self"]
        with x._eng.begin() as con:
            increment(
                con,
                x.sum_tables["remote_hourly"],
                hour,
                kwargs,
                remote=kwargs['remote_addr']
            )
            increment(
                con,
                x.sum_tables["remote_daily"],
                day,
                kwargs,
                remote=kwargs['remote_addr']
            )
            increment(
                con,
                x.sum_tables["remote_monthly"],
                month,
                kwargs,
                remote=kwargs['remote_addr']
            )

        return


######################################################
#
#   sumUserAgent
#
######################################################

if not HAS_SQLALCHEMY:

    def sumUserAgent(**kwargs):
        raise NotImplementedError("SQLAlchemy library not installed")

else:

    def sumUserAgent_set_up(*args, **kwargs):
        tables = ["useragent_hourly", "useragent_daily", "useragent_monthly"]
        create_tables(tables, **kwargs)

    def sumUserAgent(**kwargs):
        if not _check_environment(**kwargs):
            return
        if not _check_postgresql(**kwargs):
            raise NotImplementedError("Only PostgreSQL currently supported")
            return

        hour, day, month = trim_times(kwargs['date'])
        x = kwargs["_parent_self"]
        with x._eng.begin() as con:
            increment(
                con,
                x.sum_tables["useragent_hourly"],
                hour,
                kwargs,
                useragent=str(kwargs['user_agent'])
            )
            increment(
                con,
                x.sum_tables["useragent_daily"],
                day,
                kwargs,
                useragent=str(kwargs['user_agent'])
            )
            increment(
                con,
                x.sum_tables["useragent_monthly"],
                month,
                kwargs,
                useragent=str(kwargs['user_agent'])
            )

        return


######################################################
#
#   sumLanguage
#
######################################################

if not HAS_SQLALCHEMY:

    def sumLanguage(**kwargs):
        raise NotImplementedError("SQLAlchemy library not installed")

else:

    def sumLanguage_set_up(*args, **kwargs):
        tables = ["language_hourly", "language_daily", "language_monthly"]
        create_tables(tables, **kwargs)

    def sumLanguage(**kwargs):
        if not _check_environment(**kwargs):
            return
        if not _check_postgresql(**kwargs):
            raise NotImplementedError("Only PostgreSQL currently supported")
            return

        hour, day, month = trim_times(kwargs['date'])
        x = kwargs["_parent_self"]
        with x._eng.begin() as con:
            increment(
                con,
                x.sum_tables["language_hourly"],
                hour,
                kwargs,
                language=kwargs['user_agent'].language
            )
            increment(
                con,
                x.sum_tables["language_daily"],
                day,
                kwargs,
                language=kwargs['user_agent'].language
            )
            increment(
                con,
                x.sum_tables["language_monthly"],
                month,
                kwargs,
                language=kwargs['user_agent'].language
            )

        return

######################################################
#
#   sumServer
#
######################################################

if not HAS_SQLALCHEMY:

    def sumServer(**kwargs):
        raise NotImplementedError("SQLAlchemy library not installed")

else:

    def sumServer_set_up(*args, **kwargs):
        tables = ["server_hourly", "server_daily", "server_monthly"]
        create_tables(tables, **kwargs)

    def sumServer(**kwargs):
        if not _check_environment(**kwargs):
            return
        if not _check_postgresql(**kwargs):
            raise NotImplementedError("Only PostgreSQL currently supported")
            return

        hour, day, month = trim_times(kwargs['date'])
        x = kwargs["_parent_self"]
        with x._eng.begin() as con:
            increment(
                con,
                x.sum_tables["server_hourly"],
                hour,
                kwargs,
                server=kwargs["server_name"]
            )
            increment(
                con,
                x.sum_tables["server_daily"],
                day,
                kwargs,
                server=kwargs["server_name"]
            )
            increment(
                con,
                x.sum_tables["server_monthly"],
                month,
                kwargs,
                server=kwargs["server_name"]
            )

        return
