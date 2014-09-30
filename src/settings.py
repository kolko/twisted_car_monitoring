# -*- coding: utf-8 -*-
from datetime import timedelta

WEB_AGGREGATOR_PORT = 8080

#Настройки проверки таймаута
CAR_EXPIRED_LOOP_INTERVAL = 60 * 1
CAR_EXPIRED_TIME = timedelta(seconds=15)

#watcher
WATCHER_WEB_PORT = 8081
WATCHER_WEBSOCKET_PORT = 8082