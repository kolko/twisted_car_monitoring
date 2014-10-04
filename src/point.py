# -*- coding: utf-8 -*-
from math import radians, cos, sin, asin, sqrt

from tools import JsonSlotsMixin


class PositionValidationError(Exception):
    pass


class Point(JsonSlotsMixin):
    JSON_SLOTS = ['latitude', 'longitude']
    PARITY = 6
    PARITY_NUM = 10 ** PARITY

    def __init__(self, latitude, longitude):
        self._latitude = self._convert_number(latitude)
        self._longitude = self._convert_number(longitude)

    @property
    def latitude(self):
        return float(self._latitude) / self.PARITY_NUM

    @property
    def longitude(self):
        return float(self._longitude) / self.PARITY_NUM

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        if self._latitude != other._latitude:
            return False
        if self._longitude != other._longitude:
            return False
        return True

    def __sub__(self, other):
        """Distance between two points"""
        return self.distance(self, other)

    def __str__(self):
        return '{0},{1}'.format(*self.as_str_list())

    def _convert_number(self, num):
        num_int = int(float(num) * self.PARITY_NUM)
        return num_int

    def _number_as_str(self, num):
        return ('{0:0.'+str(self.PARITY)+'f}')\
            .format(float(num) / self.PARITY_NUM)

    def as_str_list(self):
        return (
            self._number_as_str(self._latitude),
            self._number_as_str(self._longitude)
        )

    def as_list_integer(self):
        return (
            self._convert_number(self._latitude),
            self._convert_number(self._longitude),
        )

    @staticmethod
    def distance(position1, position2):
        positions = (position1.latitude, position1.longitude,
                     position2.latitude, position2.longitude)
        lon1, lat1, lon2, lat2 = map(radians, positions)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        km = 6367 * c
        return km
