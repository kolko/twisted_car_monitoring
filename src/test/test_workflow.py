# -*- coding: utf-8 -*-
import pytest

from db import DB
from aggregator import Aggregator
from db import CarNotFound
from point import Point


def test_car_login_logout():
    db = DB()
    aggregator = Aggregator(db)
    car_id = aggregator.login_car()
    car = db.get_car(car_id)
    aggregator.logout_car(car_id, "Test reason")
    with pytest.raises(CarNotFound):
        db.get_car(car_id)

def test_find_near():
    db = DB()
    aggregator = Aggregator(db)
    car_id_1 = aggregator.login_car()
    car_id_2 = aggregator.login_car()
    car_id_3 = aggregator.login_car()
    car_1 = db.get_car(car_id_1)
    car_2 = db.get_car(car_id_2)
    car_3 = db.get_car(car_id_3)

    aggregator.new_position_car(car_id_1, 10, 10)
    aggregator.new_position_car(car_id_2, 20, 20)
    aggregator.new_position_car(car_id_3, 30, 30)

    assert set(db.find_near(Point(5, 5), 2)) == set([car_1, car_2])

    aggregator.logout_car(car_id_1, "Test reason")
    aggregator.logout_car(car_id_2, "Test reason")
    aggregator.logout_car(car_id_3, "Test reason")
    with pytest.raises(CarNotFound):
        db.get_car(car_id_1)
    with pytest.raises(CarNotFound):
        db.get_car(car_id_2)
    with pytest.raises(CarNotFound):
        db.get_car(car_id_3)