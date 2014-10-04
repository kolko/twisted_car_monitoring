# -*- coding: utf-8 -*-
from twisted.internet import reactor, defer


def sleep(secs):
    d = defer.Deferred()
    reactor.callLater(secs, d.callback, None)
    return d
