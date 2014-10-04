# -*- coding: utf-8 -*-
from datetime import timedelta

# порт для отправки координат автомобилями
WEB_AGGREGATOR_PORT = 8080

# Настройки проверки таймаута (запускается раз в CAR_EXPIRED_LOOP_INTERVAL секунд,
# записи, по которым не было данных более CAR_EXPIRED_TIME - удаляются)
CAR_EXPIRED_LOOP_INTERVAL = 60 * 5
CAR_EXPIRED_TIME = timedelta(minutes=1)

# Порт для подключения web-браузером
WATCHER_WEB_PORT = 8081
# Порт веб-сокета
WATCHER_WEBSOCKET_PORT = 8082
