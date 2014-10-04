# -*- coding: utf-8 -*-
from rtree import index

from car import EventDisconnect, EventUpdatePosition


class Map(object):
    """Реализует интерфейс поиска n ближайших машин
    Реализует handler для реакции на события машины (перемещение, удаление)"""
    def __init__(self):
        self.map = RtreeMap()

    def find_near(self, position, max_cars=5):
        return self.map.find_car(position, max_cars)[:max_cars]

    def handle_car(self, event, car):
        if isinstance(event, EventUpdatePosition):
            self._handle_car_new_position(
                car, event.old_position, event.new_position)
        elif isinstance(event, EventDisconnect):
            self._handle_car_logout(car)

    def _handle_car_logout(self, car):
        self.map.del_car(car.id, car.position)

    def _handle_car_new_position(self, car, old_position, new_position):
        if not old_position:
            self.map.add_car(car.id, new_position)
        else:
            if old_position != new_position:
                self.map.move_car(car.id, old_position, new_position)


class RtreeMap(object):
    def __init__(self):
        self.rtree = index.Index()

    def add_car(self, car_id, position):
        p = position.as_list_integer()
        self.rtree.insert(car_id, p * 2)

    def del_car(self, car_id, old_position):
        p = old_position.as_list_integer()
        self.rtree.delete(car_id, p * 2)

    def move_car(self, car_id, old_position, new_position):
        self.del_car(car_id, old_position)
        self.add_car(car_id, new_position)

    def find_car(self, position, count):
        return list(self.rtree.nearest(position.as_list_integer(),
                                       num_results=count))
