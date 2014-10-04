# -*- coding: utf-8 -*-
import sys

from twisted.python import log
from twisted.internet import reactor

from aggregator import register_aggregator
from watcher import register_watcher


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    register_aggregator()
    register_watcher()
    reactor.run()
