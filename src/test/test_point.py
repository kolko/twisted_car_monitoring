# -*- coding: utf-8 -*-
import pytest

from point import Point, PositionValidationError


def test_validation():
    for params in [['a', 'b'], [1, None], [None, 2], [None, None], [range(1), 1]]:
        with pytest.raises(PositionValidationError):
            Point(*params)
    for params in [[1, 1], [1, 2.33453], ['22', '22.222'], [2.2, 3.3], [0, 0], [0, 1]]:
        Point(*params)

def test_eq():
    for p1, p2 in [
        [[1, 1], [1, 1]],
        [[0, 0], [0, 0]],
        [[22.12, 22.], [22.12, 22.]],
        [[7/3., 2], [7/3., 2]]
    ]:
        assert Point(*p1) == Point(*p2)

def test_distance():
    """Актуально только для текущего алгоритма"""
    p1 = Point(1, 1)
    p2 = Point(3, 3)
    assert int(p1 - p2) == 314

def test_attributes_eq():
    for params in [[1, 1], [1, 2.33453], ['22', '22.222'], [2.2, 3.3], [0, 0], [0, 1]]:
        p = Point(*params)
        assert p.as_raw_list_integer() == (p._latitude, p._longitude)
        format = '{0:0.'+str(p.PARITY)+'f}'
        assert p.as_str_list() == (format.format(float(p._latitude) / p.PARITY_NUM),
                                    format.format(float(p._longitude) / p.PARITY_NUM))