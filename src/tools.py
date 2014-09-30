# -*- coding: utf-8 -*-
import datetime
import logging
from math import radians, cos, sin, asin, sqrt
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

def distance(position1, position2):
    lon1, lat1, lon2, lat2 = map(radians, [position1.latitude, position1.longitude,
                                           position2.latitude, position2.longitude])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))

    km = 6367 * c
    return km