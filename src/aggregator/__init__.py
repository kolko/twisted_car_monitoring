from base import Aggregator
from web_with_cookie import WebCookieAggregator


def register_aggregator():
    Aggregator.register_aggregator()
    WebCookieAggregator.register_aggregator()
