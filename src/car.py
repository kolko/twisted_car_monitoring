# -*- coding: utf-8 -*-
from datetime import datetime

from tools import JsonSlotsMixin


class CarEvent(object):
    pass


class EventDisconnect(CarEvent):
    def __init__(self, reason):
        self.reason = reason


class EventUpdatePosition(CarEvent):
    def __init__(self, old_position, new_position):
        self.old_position = old_position
        self.new_position = new_position


class Car(JsonSlotsMixin):
    JSON_SLOTS = ['id', 'position', 'last_update']
    ID_INCREMENT = 1

    def __init__(self, db):
        global I
        self.id = Car.ID_INCREMENT
        Car.ID_INCREMENT += 1
        self.db = db
        self.position = None
        self.last_update = datetime.now()
        self.handlers = []

    def __str__(self):
        return 'Car #{0} in position {1}. (last_upd {2})'.format(
            self.id, self.position, self.last_update)

    def update_position(self, new_position):
        old_position = self.position
        self.position = new_position
        self.last_update = datetime.now()
        self.notify_handlers(EventUpdatePosition(old_position, new_position))

    def logout(self, reason):
        self.notify_handlers(EventDisconnect(reason))
        self.db._handle_destroy_car(self.id)

    def add_handler(self, handler):
        if handler not in self.handlers:
            self.handlers.append(handler)

    def del_handler(self, handler):
        try:
            self.handlers.remove(handler)
        except ValueError:
            pass

    def notify_handlers(self, event):
        for handler in self.handlers:
            handler(event, self)
