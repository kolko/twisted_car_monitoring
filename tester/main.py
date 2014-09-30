# -*- coding: utf-8 -*-
import sys
import random
import json
from cookielib import CookieJar

from twisted.internet import reactor, defer, task
from twisted.python import log
from twisted.web.client import Agent, CookieAgent, readBody
from twisted.internet.protocol import Protocol

import settings
from tools import sleep


class BaseCarRider(object):
    """Базовый протокол такси-клиента"""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = 'http://{0}:{1}/'.format(self.host, self.port)
        self.agent = CookieAgent(Agent(reactor), CookieJar())

    @defer.inlineCallbacks
    def login(self):
        response = yield self.agent.request('GET', self.url + "login")
        assert response.code == 200
        body = yield readBody(response)
        data = json.loads(body)
        assert data["result"] == "ok"
        log.msg("Loggin in")

    @defer.inlineCallbacks
    def logout(self):
        response = yield self.agent.request('GET', self.url + "logout")
        assert response.code == 200
        body = yield readBody(response)
        data = json.loads(body)
        assert data["result"] == "ok"
        log.msg("Logged out")

    @defer.inlineCallbacks
    def send_location(self, w, l):
        response = yield self.agent.request('GET', self.url + "data?w={0:.6f}&l={1:.6f}".format(w, l))
        assert response.code == 200
        body = yield readBody(response)
        data = json.loads(body)
        assert data["result"] == "ok"
        log.msg("Location update success!")

    @defer.inlineCallbacks
    def work(self):
        yield task.deferLater(reactor, 0, self.login)
        w = 56835567
        l = 60590891
        while True:
            w += random.randint(-10000000, 10000000)/1000.0
            l += random.randint(-10000000, 10000000)/1000.0
            if w < 56838388:
                w = 56838388
            if w > 56839803:
                w = 56839803
            if l < 60552843:
                l = 60552843
            if l > 60574815:
                l = 60574815
            yield task.deferLater(reactor, 0, self.send_location, w/1000000.0, l/1000000.0)
            yield sleep(0.5)
        yield task.deferLater(reactor, 0, self.logout)


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    for x in xrange(100):
        car = BaseCarRider(settings.JOIN_IP, settings.JOIN_PORT)
        reactor.callLater(0, car.work)
    reactor.run()