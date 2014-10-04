# -*- coding: utf-8 -*-
import json
from datetime import datetime

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log

import settings
from db import DB, CarNotFound
from tools import debug_log
from point import Point, PositionValidationError


class Aggregator(object):
    """Принимает данные с машин"""
    # TODO: выпилить синглтоны
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Aggregator, cls).\
                __new__(cls, *args, **kwargs)
        return cls._instance

    def login_car(self):
        """Новый автомобиль"""
        car = DB().create_car()
        return car.id

    def logout_car(self, car_id, reason="Normal logout from aggregator"):
        car = DB().get_car(car_id)
        car.logout(reason)

    def new_position_car(self, car_id, latitude, longitude):
        car = DB().get_car(car_id)
        position = Point(latitude, longitude)
        car.update_position(position)

    def test_cars_by_update_time_expired(self):
        debug_log("Run test_cars_by_update_time_expired")
        for car in DB().get_all_cars():
            if car.last_update < datetime.now() - settings.CAR_EXPIRED_TIME:
                debug_log("Drop car by timeout {0}".format(car))
                self.logout_car(car.id, "Logout by timeout")
        reactor.callLater(settings.CAR_EXPIRED_LOOP_INTERVAL,
                          self.test_cars_by_update_time_expired)

    @staticmethod
    def register_aggregator():
        reactor.callLater(settings.CAR_EXPIRED_LOOP_INTERVAL,
                          Aggregator().test_cars_by_update_time_expired)
