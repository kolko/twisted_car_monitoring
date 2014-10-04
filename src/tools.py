# -*- coding: utf-8 -*-
import datetime
import logging
from twisted.python import log


def debug_log(msg):
    log.msg(msg, logLevel=logging.DEBUG)


class JsonSlotsMixin(object):
    def data_as_json(self):
        data = {}
        for attr in self.JSON_SLOTS:
            obj = getattr(self, attr, None)
            if issubclass(obj.__class__, JsonSlotsMixin):
                obj = obj.data_as_json()
            if isinstance(obj, datetime.datetime) \
                    or isinstance(obj, datetime.date):
                obj = obj.isoformat()
            data[attr] = obj
        return data
