from logics import Value


def test_conversion():
    assert Value({"a": 1}) == Value({"a": 1})
    assert Value(4) == Value(4)
    assert Value(4) != 2
    assert Value(4) + 4 == 8
    assert repr(Value("4112", optimize=True)) == "4112"


def test_none():
    none = Value(None)
    assert none == None
    assert bool(none) == False
    assert int(none) == 0
    assert float(none) == 0.0
    assert repr(none) == "None"


def test_bool():
    true = Value(True)
    false = Value(False)
    assert true == True
    assert false == False
    assert true == 1
    assert false == 0
    assert int(true) == 1
    assert int(false) == 0
    assert repr(true) == "True"
    assert repr(false) == "False"


def test_int():
    _123 = Value(123)
    assert _123 == 123
    assert -_123 == -123
    assert int(Value(" 123 xix")) == 123
    assert int(Value(" -123 xix")) == -123
    assert repr(_123) == "123"
    assert repr(-_123) == "-123"


def test_float():
    _1234 = Value(123.4)
    assert Value(_1234) == 123.4
    assert Value(-_1234) == -123.4
    assert float(Value(" 123.4 xfx")) == 123.4
    assert float(Value(" -123.4 xfx")) == -123.4
    assert repr(_1234) == "123.4"
    assert repr(-_1234) == "-123.4"
