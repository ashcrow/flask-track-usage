import datetime
try:
    import mongoengine as db
    MONGOENGINE_MISSING = False
except ImportError:
    MONGOENGINE_MISSING = True


def _check_environment(**kwargs):
    if MONGOENGINE_MISSING:
        return False
    if 'mongoengine_document' not in kwargs:
        return False
    return True


def trim_times(date):
    hour = date.replace(minute=0, second=0, microsecond=0)
    day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return hour, day, month


def trim_times_dict(date):
    h, d, m = trim_times(date)
    return {"hour": h, "day": d, "month": m}


def increment(class_dict, src, dest, target_list):
    times = trim_times_dict(src.date)
    db_args = {}
    if dest:
        value = src
        for key in target_list:
            value = value[key]
        db_args[dest] = value
    for period in ["hour", "day", "month"]:
        doc = class_dict[period].objects(date=times[period], **db_args).first()
        if not doc:
            doc = class_dict[period]()
            doc.date = times[period]
            if dest:
                doc[dest] = value
        doc.hits += 1
        if src.content_length:
            doc.transfer += src.content_length
            doc.save()


def generic_get_sum(
        class_dict,
        key,
        start_date=None,
        end_date=None,
        limit=500,
        page=1,
        target=None,
        _parent_class_name=None,
        _parent_self=None
):
    # note: for mongoegine, we can ignore _parent* parms as the module
    # is global
    final = {}
    query = {}
    if start_date and not end_date:
        normal_startstop = trim_times_dict(start_date)
    else:
        if start_date:
            query["date__gte"] = start_date
        if end_date:
            query["date__lte"] = end_date
    if target is not None:
        query[key] = target
    for period in class_dict.keys():
        if start_date and not end_date:
            query["date"] = normal_startstop[period]
        if limit:
            first = limit * (page - 1)
            last = limit * page
            logs = class_dict[period].objects(
                **query
            ).order_by('-date')[first:last]
        else:
            logs = class_dict[period].objects(**query).order_by('-date')
        final[period] = [log.to_mongo().to_dict() for log in logs]
    return final


######################################################
#
#   sumURL
#
######################################################

if MONGOENGINE_MISSING:

    def sumUrl(**kwargs):
        raise NotImplementedError("MongoEngine library not installed")

else:

    class UsageTrackerSumUrlHourly(db.Document):
        url = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumUrl_hourly"
        }

    class UsageTrackerSumUrlDaily(db.Document):
        url = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumUrl_daily"
        }

    class UsageTrackerSumUrlMonthly(db.Document):
        url = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumUrl_monthly"
        }

    sumUrlClasses = {
        "hour": UsageTrackerSumUrlHourly,
        "day": UsageTrackerSumUrlDaily,
        "month": UsageTrackerSumUrlMonthly,
    }

    def sumUrl(**kwargs):
        if not _check_environment(**kwargs):
            return
        src = kwargs['mongoengine_document']
        #
        increment(sumUrlClasses, src, "url", ["url"])
        return

    def sumUrl_get_sum(**kwargs):
        return generic_get_sum(sumUrlClasses, "url", **kwargs)

######################################################
#
#   sumRemote
#
######################################################

if MONGOENGINE_MISSING:

    def sumRemote(**kwargs):
        raise NotImplementedError("MongoEngine library not installed")

else:

    class UsageTrackerSumRemoteHourly(db.Document):
        remote_addr = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumRemote_hourly"
        }

    class UsageTrackerSumRemoteDaily(db.Document):
        remote_addr = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumRemote_daily"
        }

    class UsageTrackerSumRemoteMonthly(db.Document):
        remote_addr = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumRemote_monthly"
        }

    sumRemoteClasses = {
        "hour": UsageTrackerSumRemoteHourly,
        "day": UsageTrackerSumRemoteDaily,
        "month": UsageTrackerSumRemoteMonthly,
    }

    def sumRemote(**kwargs):
        if not _check_environment(**kwargs):
            return
        src = kwargs['mongoengine_document']
        #
        increment(sumRemoteClasses, src, "remote_addr", ["remote_addr"])
        return

    def sumRemote_get_sum(**kwargs):
        return generic_get_sum(sumRemoteClasses, "remote_addr", **kwargs)

######################################################
#
#   sumUserAgent
#
######################################################

if MONGOENGINE_MISSING:

    def sumUserAgent(**kwargs):
        raise NotImplementedError("MongoEngine library not installed")

else:

    class UsageTrackerSumUserAgentHourly(db.Document):
        user_agent_string = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumUserAgent_hourly"
        }

    class UsageTrackerSumUserAgentDaily(db.Document):
        user_agent_string = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumUserAgent_daily"
        }

    class UsageTrackerSumUserAgentMonthly(db.Document):
        user_agent_string = db.StringField()
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumUserAgent_monthly"
        }

    sumUserAgentClasses = {
        "hour": UsageTrackerSumUserAgentHourly,
        "day": UsageTrackerSumUserAgentDaily,
        "month": UsageTrackerSumUserAgentMonthly,
    }

    def sumUserAgent(**kwargs):
        if not _check_environment(**kwargs):
            return
        src = kwargs['mongoengine_document']
        #
        increment(
            sumUserAgentClasses,
            src,
            "user_agent_string",
            ["user_agent", "string"]
        )
        return

    def sumUserAgent_get_sum(**kwargs):
        return generic_get_sum(
            sumUserAgentClasses,
            "user_agent_string",
            **kwargs
        )

######################################################
#
#   sumLanguage
#
######################################################

if MONGOENGINE_MISSING:

    def sumLanguage(**kwargs):
        raise NotImplementedError("MongoEngine library not installed")

else:

    class UsageTrackerSumLanguageHourly(db.Document):
        language = db.StringField(null=True)
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumLanguage_hourly"
        }

    class UsageTrackerSumLanguageDaily(db.Document):
        language = db.StringField(null=True)
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumLanguage_daily"
        }

    class UsageTrackerSumLanguageMonthly(db.Document):
        language = db.StringField(null=True)
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumLanguage_monthly"
        }

    sumLanguageClasses = {
        "hour": UsageTrackerSumLanguageHourly,
        "day": UsageTrackerSumLanguageDaily,
        "month": UsageTrackerSumLanguageMonthly,
    }

    def sumLanguage(**kwargs):
        if not _check_environment(**kwargs):
            return
        src = kwargs['mongoengine_document']
        #
        if not src.user_agent.language:
            src.user_agent.language = "none"
        increment(
            sumLanguageClasses,
            src,
            "language",
            ["user_agent", "language"]
        )
        return

    def sumLanguage_get_sum(**kwargs):
        return generic_get_sum(sumLanguageClasses, "language", **kwargs)

######################################################
#
#   sumServer
#
######################################################

if MONGOENGINE_MISSING:

    def sumServer(**kwargs):
        raise NotImplementedError("MongoEngine library not installed")

else:

    class UsageTrackerSumServerHourly(db.Document):
        server_name = db.StringField(default="self")
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumServer_hourly"
        }

    class UsageTrackerSumServerDaily(db.Document):
        server_name = db.StringField(default="self")
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumServer_daily"
        }

    class UsageTrackerSumServerMonthly(db.Document):
        server_name = db.StringField(default="self")
        date = db.DateTimeField(required=True)
        hits = db.IntField(requried=True, default=0)
        transfer = db.IntField(required=True, default=0)
        meta = {
            'collection': "usageTracking_sumServer_monthly"
        }

    sumServerClasses = {
        "hour": UsageTrackerSumServerHourly,
        "day": UsageTrackerSumServerDaily,
        "month": UsageTrackerSumServerMonthly,
    }

    def sumServer(**kwargs):
        if not _check_environment(**kwargs):
            return
        src = kwargs['mongoengine_document']
        #
        increment(sumServerClasses, src, "server_name", ["server_name"])
        return

    def sumServer_get_sum(**kwargs):
        return generic_get_sum(sumServerClasses, "server_name", **kwargs)
