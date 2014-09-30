# -*- coding: utf-8 -*-
import sys

from twisted.python import log
from twisted.internet import reactor

from aggregator import WebAggregator
from watcher import register_watcher



class Finder(object):
    """Позволяет отыскать автомобиль"""
    pass



if __name__ == "__main__":
    log.startLogging(sys.stdout)
    WebAggregator.register_web_aggregator()
    register_watcher()
    reactor.run()