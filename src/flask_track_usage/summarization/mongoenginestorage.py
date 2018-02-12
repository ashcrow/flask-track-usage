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
    hour = date.replace(minute=0, second=0)
    day = date.replace(hour=0, minute=0, second=0)
    month = date.replace(day=1, hour=0, minute=0, second=0)
    return hour, day, month


def increment(class_dict, src, dest, target_list):
    times = {}
    times["hour"], times["day"], times["month"] = trim_times(src.date)
    value = src
    for key in target_list:
        value = value[key]
    kwargs = {dest: value}
    for period in ["hour", "day", "month"]:
        doc = class_dict[period].objects(date=times[period], **kwargs).first()
        if not doc:
            doc = class_dict[period]()
            doc.date = times[period]
            doc[dest] = value
        doc.hits += 1
        doc.transfer += src.content_length
        doc.save()


######################################################
#
#   sumURL
#
######################################################

if not MONGOENGINE_MISSING:

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


######################################################
#
#   sumRemote
#
######################################################

if not MONGOENGINE_MISSING:

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


######################################################
#
#   sumUserAgent
#
######################################################

if not MONGOENGINE_MISSING:

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
    increment(sumUserAgentClasses, src, "user_agent_string", ["user_agent", "string"])
    return


# def sumLanguage(**kwargs):
#     if not _check_environment(**kwargs):
#         return
#     src = kwargs['mongoengine_document']
#     #
#     increment(sumUrlClasses, src, ["user_agent", "language"])
#     return


# def sumServer(**kwargs):
#     if not _check_environment(**kwargs):
#         return
#     src = kwargs['mongoengine_document']
#     #
#     increment(sumUrlClasses, src, None)
#     return
