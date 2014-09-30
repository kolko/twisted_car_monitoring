# -*- coding: utf-8 -*-
import json
from datetime import datetime

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log

import settings
from db import DB, Point, CarNotFound
from tools import debug_log


class Aggregator(object):
    """Принимает данные с машин"""
    #TODO: выпилить синглтоны
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Aggregator, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def login_car(self):
        """Новый автомобиль"""
        car = DB().create_car()
        return car.id

    def logout_car(self, car_id, reason="Normal logout from aggregator"):
        car = DB().get_car(car_id)
        car.logout(reason)

    def new_position_car(self, car_id, position):
        car = DB().get_car(car_id)
        car.update_position(position)

    def test_cars_by_update_time_expired(self):
        debug_log("Run test_cars_by_update_time_expired")
        for car in DB().get_all_cars():
            if car.last_update < datetime.now() - settings.CAR_EXPIRED_TIME:
                debug_log("Drop car by timeout {0}".format(car))
                self.logout_car(car.id, "Logout by timeout")
        reactor.callLater(settings.CAR_EXPIRED_LOOP_INTERVAL, self.test_cars_by_update_time_expired)


class WebAggregator(resource.Resource):
    """Веб-сервер
    Функционал:
    1.Залогинить, выдать сессию
    2.Собирать трек
    3.Разлогинить
    """
    isLeaf = True

    def render_GET(self, request):
        if request.path == "/login":
            return self.car_login(request)
        if request.path == "/logout":
            return self.car_logout(request)
        if request.path == "/data":
            return self.car_data(request)
        return self.json_err("Not found 404")

    def car_login(self, request):
        session = request.getSession()
        car_id = getattr(session, "car_id", None)
        if car_id:
            debug_log("Double login")
            return self.json_err("Already logged")
        car_id = Aggregator().login_car()
        session.car_id = car_id
        debug_log("Logged new car id: {0}".format(car_id))
        return self.json_ok()

    def car_logout(self, request):
        session = request.getSession()
        car_id = getattr(session, "car_id", None)
        if not car_id:
            debug_log("Try logout without car_id in session")
            self.json_err("Already logged out")
        session.expire()
        try:
            Aggregator().logout_car(car_id)
        except CarNotFound:
            pass
        debug_log("Logged out car id: {0}".format(car_id))
        return self.json_ok()

    def car_data(self, request):
        session = request.getSession()
        car_id = getattr(session, "car_id", None)
        if not car_id:
            debug_log("Try put data without session")
            self.json_err("You must login first")
        w = request.args.get('w')[0]
        l = request.args.get('l')[0]
        position = Point(w, l)
        #todo validate w and l
        debug_log("Update position {0}: {1}".format(car_id, position))
        try:
            Aggregator().new_position_car(car_id, position)
        except CarNotFound:
            session.expire()
            return self.json_err("You must login first")
        return self.json_ok()

    @staticmethod
    def register_web_aggregator():
        web_aggregator = server.Site(WebAggregator())
        reactor.listenTCP(settings.WEB_AGGREGATOR_PORT, web_aggregator)
        #todo: move from here
        reactor.callLater(settings.CAR_EXPIRED_LOOP_INTERVAL, Aggregator().test_cars_by_update_time_expired)

    @staticmethod
    def json_err(msg):
        return json.dumps({"error": msg})

    @staticmethod
    def json_ok():
        return json.dumps({"result": "ok"})