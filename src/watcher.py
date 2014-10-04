# -*- coding: utf-8 -*-
import json
from string import Template

from twisted.python import log
from twisted.internet import reactor
from twisted.web import server, resource

from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory

import settings
from db import DB, CarNotFound
from car import EventUpdatePosition, EventDisconnect
from point import Point
from point import PositionValidationError
from tools import debug_log


class WatcherSite(resource.Resource):
    isLeaf = True

    def render_GET(self, request):
        if request.path == "/":
            return self.list_all_cars()
        if request.path == "/watch_car":
            return self.watch_car(request)
        if request.path == "/get_near":
            return self.get_near(request)
        return "404"

    def list_all_cars(self):
        return ''.join(
            "<p><a href='/watch_car?car_id={0}'>{1}</a>".format(car.id, car)
            for car in DB().get_all_cars()
        )

    def watch_car(self, request):
        car_id = request.args.get('car_id', None)
        if not car_id or not car_id[0].isdigit():
            return "Not found"
        car_id = int(car_id[0])
        db = DB()
        try:
            car = db.get_car(car_id)
        except CarNotFound:
            return "Not found"
        with open('html/watch_car_websocket.html', 'r') as f:
            html = f.read()
        socket_port = settings.WATCHER_WEBSOCKET_PORT
        html = Template(html).substitute({
            'car_id': car.id,
            'socket_port': str(socket_port)
        })
        return html

    def get_near(self, request):
        latitude = request.args['latitude'][0]
        longitude = request.args['longitude'][0]
        format_json = request.args.get('json', None)
        try:
            position = Point(latitude, longitude)
        except PositionValidationError:
            return "Bad position"
        db = DB()
        if format_json:
            res = [car.data_as_json() for car in db.find_near(position)]
            return json.dumps(res)
        return ''.join(
            "<p><a href='/watch_car?car_id={0}'>{1} {distance:0.3f} km</a>".format(
                car.id, car, distance=position - car.position
            )
            for car in db.find_near(position)
        )


class WatcherWebsocket(WebSocketServerProtocol):
    def __init__(self):
        self.car = None

    def onConnect(self, request):
        if request.path != '/watch_car':
            self.closedByMe()
        car_id = request.params.get('car_id', None)
        if not car_id or not car_id[0].isdigit():
            self.closedByMe()
        car_id = int(car_id[0])
        self.car = DB().get_car(car_id)
        self.car.add_handler(self._event_handler)
        debug_log("Websocket connect for car: {0}".format(self.car))

    def onClose(self, wasClean, code, reason):
        debug_log("WebSocket connection closed: {0}".format(reason))
        if self.car:
            self.car.del_handler(self._event_handler)
        self.car = None

    def _event_handler(self, event, car):
        assert car == self.car
        debug_log("Alert {0} from car: {1}".format(event, car))

        if isinstance(event, EventUpdatePosition):
            res = {
                "event": "position_update",
                "position": event.new_position.data_as_json(),
            }
            self.sendMessage(json.dumps(res))
        elif isinstance(event, EventDisconnect):
            res = {"event": "car_disconnect"}
            d = self.sendMessage(json.dumps(res))
            if d:
                d.addCallback(self.closedByMe)


def register_watcher():
    site = server.Site(WatcherSite())
    reactor.listenTCP(settings.WATCHER_WEB_PORT, site)

    port = settings.WATCHER_WEBSOCKET_PORT
    url = "ws://{0}:{1}".format('127.0.0.1', port)
    factory = WebSocketServerFactory(url, debug=False)
    factory.protocol = WatcherWebsocket
    reactor.listenTCP(port, factory)
