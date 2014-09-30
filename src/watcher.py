# -*- coding: utf-8 -*-
import json
from string import Template

from twisted.python import log
from twisted.internet import reactor
from twisted.web import server, resource

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

import settings
from db import DB, Point, CarNotFound
from db import EventUpdatePosition, EventDisconnect
from tools import debug_log


class Watcher(object):
    """Позволяет следить за конкретным автомобилем"""
    pass

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
        res_html = ""
        db = DB()
        for car in db.get_all_cars():
            res_html += "<p><a href='/watch_car?car_id={0}'>{1}</a>".format(car.uid, car)
        return res_html

    def watch_car(self, request):
        car_id = request.args.get('car_id', None)
        if not car_id:
            return "Not found"
        car_id = car_id[0]
        db = DB()
        try:
            car = db.get_car(car_id)
        except CarNotFound:
            return "Not found"
        with open('html/watch_car_websocket.html', 'r') as f:
            html = f.read()
        socket_port = settings.WATCHER_WEBSOCKET_PORT
        html = Template(html).substitute({'car_id': car.uid,
                            'socket_port': str(socket_port)})
        return html

    def get_near(self, request):
        latitude = request.args['latitude'][0]
        longitude = request.args['longitude'][0]
        position = Point(latitude, longitude)
        res_html = ""
        db = DB()
        for car in db.find_near(position):
            res_html += "<p><a href='/watch_car?car_id={0}'>{1}</a>".format(car.uid, car)
        return res_html


class WatcherWebsocket(WebSocketServerProtocol):
    def __init__(self):
        self.car_id = None

    def onConnect(self, request):
        if request.path != '/watch_car':
            self.closedByMe()
        car_id = request.params.get('car_id', None)
        if not car_id or not car_id[0].is_digit():
            self.closedByMe()
        self.car_id = int(car_id[0])
        db = DB()
        db.register_handler(self.car_id, self._event_handler)
        debug_log("Websocket connect for car_id: {0}".format(self.car_id))

    def onClose(self, wasClean, code, reason):
        debug_log("WebSocket connection closed: {0}".format(reason))

    def _event_handler(self, event, car_id):
        assert car_id == self.car_id
        debug_log("Alert {0} from car_id: {1}".format(event, car_id))
        if isinstance(event, EventUpdatePosition):
            res = {"event": "position_update", "position": event.position.data_as_json()}
            self.sendMessage(json.dumps(res))
        if isinstance(event, EventDisconnect):
            res = {"event": "car_disconnect"}
            d = self.sendMessage(json.dumps(res))
            d.addCallback(self.closedByMe)

def register_watcher():
    site = server.Site(WatcherSite())
    reactor.listenTCP(settings.WATCHER_WEB_PORT, site)

    port = settings.WATCHER_WEBSOCKET_PORT
    factory = WebSocketServerFactory("ws://{0}:{1}".format('127.0.0.1', port), debug=False)
    factory.protocol = WatcherWebsocket
    reactor.listenTCP(port, factory)