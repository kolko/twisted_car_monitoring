# -*- coding: utf-8 -*-
import json
from datetime import datetime

from car import Car
from map import Map


class CarNotFound(Exception):
    pass


class DB(object):
    # TODO: выпилить синглтоны
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DB, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not getattr(self, 'car_storage', None):
            self.car_storage = {}
            self.map = Map()

    def create_car(self):
        new_car = Car(self)
        self.car_storage[new_car.id] = new_car
        new_car.add_handler(self.map.handle_car)
        return new_car

    def get_car(self, car_id):
        car = self.car_storage.get(car_id, None)
        if not car:
            raise CarNotFound()
        return car

    def get_all_cars(self):
        return self.car_storage.values()

    def find_near(self, position, max_cars=5):
        return map(self.car_storage.get,
                   self.map.find_near(position, max_cars))
