# -*- coding: utf-8 -*-
import sys

from twisted.python import log
from twisted.internet import reactor

from aggregator import WebAggregator
from watcher import register_watcher


if __name__ == "__main__":
    # log.startLogging(sys.stdout)
    WebAggregator.register_web_aggregator()
    register_watcher()
    reactor.run()