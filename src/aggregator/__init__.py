from twisted.internet import reactor

from base import Aggregator
from web_with_cookie import WebCookieAggregator
import settings


def register_aggregator(db):
    aggregator = Aggregator(db)
    reactor.callLater(settings.CAR_EXPIRED_LOOP_INTERVAL,
                          aggregator.test_cars_by_update_time_expired)
    WebCookieAggregator.register_aggregator(aggregator)