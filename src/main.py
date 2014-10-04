# -*- coding: utf-8 -*-
import sys

from twisted.python import log
from twisted.internet import reactor

from aggregator import register_aggregator
from watcher import register_watcher
from db import DB


if __name__ == "__main__":
    # log.startLogging(sys.stdout)
    db = DB()
    register_aggregator(db)
    register_watcher(db)
    reactor.run()
