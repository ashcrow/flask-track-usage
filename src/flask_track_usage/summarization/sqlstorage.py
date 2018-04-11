import datetime
try:
    import sqlalchemy as sql
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False


def _check_environment(**kwargs):
    if not HAS_SQLALCHEMY:
        return False
    return True


# def trim_times(date):
#     hour = date.replace(minute=0, second=0, microsecond=0)
#     day = date.replace(hour=0, minute=0, second=0, microsecond=0)
#     month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#     return hour, day, month


# def increment(class_dict, src, dest, target_list):
#     times = {}
#     times["hour"], times["day"], times["month"] = trim_times(src.date)
#     db_args = {}
#     if dest:
#         value = src
#         for key in target_list:
#             value = value[key]
#         db_args[dest] = value
#     for period in ["hour", "day", "month"]:
#         doc = class_dict[period].objects(date=times[period], **db_args).first()
#         if not doc:
#             doc = class_dict[period]()
#             doc.date = times[period]
#             if dest:
#                 doc[dest] = value
#         doc.hits += 1
#         doc.transfer += src.content_length
#         doc.save()


######################################################
#
#   sumURL
#
######################################################

if not HAS_SQLALCHEMY:

    def sumUrl(**kwargs):
        raise NotImplementedError("SQLAlchemy library not installed")

else:

    # class UsageTrackerSumUrlHourly(db.Document):
    #     url = db.StringField()
    #     date = db.DateTimeField(required=True)
    #     hits = db.IntField(requried=True, default=0)
    #     transfer = db.IntField(required=True, default=0)
    #     meta = {
    #         'collection': "usageTracking_sumUrl_hourly"
    #     }

    # class UsageTrackerSumUrlDaily(db.Document):
    #     url = db.StringField()
    #     date = db.DateTimeField(required=True)
    #     hits = db.IntField(requried=True, default=0)
    #     transfer = db.IntField(required=True, default=0)
    #     meta = {
    #         'collection': "usageTracking_sumUrl_daily"
    #     }

    # class UsageTrackerSumUrlMonthly(db.Document):
    #     url = db.StringField()
    #     date = db.DateTimeField(required=True)
    #     hits = db.IntField(requried=True, default=0)
    #     transfer = db.IntField(required=True, default=0)
    #     meta = {
    #         'collection': "usageTracking_sumUrl_monthly"
    #     }

    # sumUrlClasses = {
    #     "hour": UsageTrackerSumUrlHourly,
    #     "day": UsageTrackerSumUrlDaily,
    #     "month": UsageTrackerSumUrlMonthly,
    # }

    def sumUrl(**kwargs):
        if not _check_environment(**kwargs):
            return
        # TODO: open the three summary URL tables and increment the correct rows

        # src = kwargs['mongoengine_document']
        #
        # increment(sumUrlClasses, src, "url", ["url"])
        return


######################################################
#
#   sumRemote
#
######################################################


######################################################
#
#   sumUserAgent
#
######################################################


######################################################
#
#   sumLanguage
#
######################################################


######################################################
#
#   sumServer
#
######################################################

