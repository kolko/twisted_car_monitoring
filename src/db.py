# -*- coding: utf-8 -*-
import uuid
import json
from datetime import datetime

from rtree import index

from tools import JsonSlotsMixin

#EXCEPTIONS
class CarNotFound(Exception):
    pass

#EVENTS
class CarEvent(object):
    pass


class EventDisconnect(CarEvent):
    def __init__(self, reason):
        self.reason = reason


class EventUpdatePosition(CarEvent):
    def __init__(self, old_position, new_position):
        self.old_position = old_position
        self.new_position = new_position

I = 1
#CODE
class Car(JsonSlotsMixin):
    JSON_SLOTS = ['id', 'position', 'last_update']
    def __init__(self, db):
        global I
        self.id = I #uuid.uuid4()
        I += 1
        self.db = db
        self.position = None
        self.last_update = datetime.now()
        self.handlers = []

    def __str__(self):
        return 'Car #{0} in position {1}. (last_upd {2})'.format(self.id,
                                                                 self.position,
                                                                 self.last_update)

    def update_position(self, new_position):
        old_position = self.position
        self.position = new_position
        self.last_update = datetime.now()
        self.notify_handlers(EventUpdatePosition(old_position, new_position))

    def logout(self, reason):
        self.notify_handlers(EventDisconnect(reason))

    def add_handler(self, handler):
        if handler not in self.handlers:
            self.handlers.append(handler)

    def del_handler(self, handler):
        try:
            self.handlers.remove(handler)
        except ValueError:
            pass

    def notify_handlers(self, event):
        for h in self.handlers:
            h(event, self)


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
        return self._latitude, self._longitude == other._latitude, other._longitude

    def __str__(self):
        return '{0},{1}'.format(*self.as_str_list())

    def _convert_number(self, num):
        num_int = int(float(num) * self.PARITY_NUM)
        return num_int

    def _number_as_str(self, num):
        return ('{0:0.'+str(self.PARITY)+'f}').format(float(num) / self.PARITY_NUM)

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


class DB(object):
    """База данных всех автомобилей
    """
    #TODO: выпилить синглтоны
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
        new_car.add_handler(self._handle_car)
        return new_car

    def get_car(self, car_id):
        car = self.car_storage.get(car_id, None)
        if not car:
            raise CarNotFound()
        return car

    def get_all_cars(self):
        return self.car_storage.values()

    def find_near(self, position, count=5):
        return map(self.car_storage.get, self.map.find_car(position, count))[:count]

    def _handle_car(self, event, car):
        if isinstance(event, EventUpdatePosition):
            self._handle_car_new_position(car, event.old_position, event.new_position)
        if isinstance(event, EventDisconnect):
            self._handle_car_logout(car)

    def _handle_car_logout(self, car):
        self.map.del_car(car.id, car.position)
        del self.car_storage[car.id]

    def _handle_car_new_position(self, car, old_position, new_position):
        if not old_position:
            self.map.add_car(car.id, new_position)
        else:
            if old_position != new_position:
                self.map.move_car(car.id, old_position, new_position)


class Map(object):
    def __init__(self):
        self.map = index.Index()

    def add_car(self, car_id, position):
        p = position.as_list_integer()
        self.map.insert(car_id, p * 2)

    def del_car(self, car_id, old_position):
        p = old_position.as_list_integer()
        self.map.delete(car_id, p * 2)

    def move_car(self, car_id, old_position, new_position):
        self.del_car(car_id, old_position)
        self.add_car(car_id, new_position)

    def find_car(self, position, count):
        return list(self.map.nearest(position.as_list_integer(), num_results=count))