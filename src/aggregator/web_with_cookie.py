# -*- coding: utf-8 -*-
import json
from datetime import datetime

from twisted.web import server, resource
from twisted.internet import reactor
from twisted.python import log

import settings
from tools import debug_log
from base import CarNotFound, PositionValidationError


class WebCookieAggregator(resource.Resource):
    isLeaf = True

    def __init__(self, aggregator):
        self._aggregator = aggregator

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
        car_id = self._aggregator.login_car()
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
            self._aggregator.logout_car(car_id)
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
        latitude = request.args.get('latitude', None)
        longitude = request.args.get('longitude', None)
        if not (latitude and longitude):
            return self.json_err("Bad position!")
        latitude = latitude[0]
        longitude = longitude[0]
        debug_log("Update position {0}: {1} {2}".
                  format(car_id, latitude, longitude))
        try:
            self._aggregator.new_position_car(car_id, latitude, longitude)
        except CarNotFound:
            session.expire()
            return self.json_err("You must login first")
        except PositionValidationError:
            return self.json_err("Bad position!")
        return self.json_ok()

    @staticmethod
    def json_err(msg):
        return json.dumps({"error": msg})

    @staticmethod
    def json_ok():
        return json.dumps({"result": "ok"})

    @staticmethod
    def register_aggregator(aggregator):
        web_aggregator = server.Site(WebCookieAggregator(aggregator))
        reactor.listenTCP(settings.WEB_AGGREGATOR_PORT, web_aggregator)
