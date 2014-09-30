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
    pass


class EventUpdatePosition(CarEvent):
    def __init__(self, position):
        self.position = position

I = 1
#CODE
class Car(object, JsonSlotsMixin):
    JSON_SLOTS = ['id', 'position', 'last_update']
    def __init__(self):
        global I
        self.id = I #uuid.uuid4()
        I += 1
        self.position = None
        self.last_update = None
        self.handlers = []
        self.on_map = False

    def __str__(self):
        return 'Car #{0} in position {1}. (last_upd {2})'.format(self.id,
                                                                 self.position,
                                                                 self.last_update)

    def update_position(self, position):
        self.position = position
        self.last_update = datetime.now()

    def add_handler(self, handler):
        self.handlers.append(handler)

    def del_handler(self, handler):
        self.handlers.remove(handler)

    def notify_handlers(self, event):
        for h in self.handlers:
            h(event, self.id)


class Point(object, JsonSlotsMixin):
    JSON_SLOTS = ['latitude', 'longitude']
    PARITY = 6
    PARITY_NUM = 10 ** PARITY

    def __init__(self, latitude, longitude):
        self.latitude = self._convert_number(latitude)
        self.longitude = self._convert_number(longitude)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.latitude, self.longitude == other.latitude, other.longitude

    def __str__(self):
        return '{0},{1}'.format(*self.as_str_list())

    def _convert_number(self, num):
        num_int = int(float(num) * self.PARITY_NUM)
        return num_int

    def _number_as_str(self, num):
        return ('{0:0.'+str(self.PARITY)+'f}').format(float(num) / self.PARITY_NUM)

    def as_str_list(self):
        return (
            self._number_as_str(self.latitude),
            self._number_as_str(self.longitude)
        )

    def as_list_integer(self):
        return (
            self._convert_number(self.latitude),
            self._convert_number(self.longitude),
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
        new_car = Car()
        self.car_storage[new_car.id] = new_car
        return new_car.id

    def logout_car(self, car_id):
        car = self.car_storage.pop(car_id, None)
        if not car:
            raise CarNotFound()
        self.map.del_car(car.uid, car.position)
        car.notify_handlers(EventDisconnect())

    def new_position_car(self, car_id, position):
        car = self.car_storage.get(car_id, None)
        if not car:
            raise CarNotFound()
        if not car.on_map:
            self.map.add_car(car.uid, position)
            car.on_map = True
        else:
            self.map.move_car(car.uid, car.position, position)
        car.update_position(position)
        car.notify_handlers(EventUpdatePosition(position))

    def get_car(self, car_id):
        car = self.car_storage.get(car_id, None)
        if not car:
            raise CarNotFound()
        return car

    def get_car_position(self, car_id):
        car = self.car_storage.get(car_id, None)
        if not car:
            raise CarNotFound()
        return car.position

    def get_car_last_update(self, car_id):
        car = self.car_storage.get(car_id, None)
        if not car:
            raise CarNotFound()
        return car.last_update

    def get_all_cars(self):
        return self.car_storage.values()

    def register_handler(self, car_id, handler):
        car = self.car_storage.get(car_id, None)
        if not car:
            raise CarNotFound()
        car.add_handler(handler)

    def find_near(self, position, count=5):
        return map(self.car_storage.get, self.map.find_car(position, count))


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