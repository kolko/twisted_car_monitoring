# -*- coding: utf-8 -*-
from datetime import datetime

from twisted.internet import reactor
from twisted.python import log

import settings
from db import CarNotFound
from tools import debug_log
from point import Point, PositionValidationError


class Aggregator(object):
    """Принимает данные с машин"""
    def __init__(self, db):
        self._db = db

    def login_car(self):
        """Новый автомобиль"""
        car = self._db.create_car()
        return car.id

    def logout_car(self, car_id, reason="Normal logout from aggregator"):
        car = self._db.get_car(car_id)
        car.logout(reason)

    def new_position_car(self, car_id, latitude, longitude):
        car = self._db.get_car(car_id)
        position = Point(latitude, longitude)
        car.update_position(position)

    def test_cars_by_update_time_expired(self):
        debug_log("Run test_cars_by_update_time_expired")
        for car in self._db.get_all_cars():
            if car.last_update < datetime.now() - settings.CAR_EXPIRED_TIME:
                debug_log("Drop car by timeout {0}".format(car))
                self.logout_car(car.id, "Logout by timeout")
        reactor.callLater(settings.CAR_EXPIRED_LOOP_INTERVAL,
                          self.test_cars_by_update_time_expired)
