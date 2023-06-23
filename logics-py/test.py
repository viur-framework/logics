from logics import Logics, Value
import unittest


class ValueTestCase(unittest.TestCase):

    def test_conversion(self):
        self.assertTrue(Value({"a": 1} != Value({"a": 1})))
        self.assertTrue(Value(4) == Value(4))
        self.assertFalse(Value(4) == 2)
        self.assertEqual(Value(4) + 4, 8)
        self.assertEqual(repr(Value("4112", optimize=True)), "4112")

    def test_none(self):
        none = Value(None)
        self.assertEqual(none, None)
        self.assertEqual(bool(none), False)
        self.assertEqual(int(none), 0)
        self.assertEqual(float(none), 0.0)
        self.assertEqual(repr(none), "None")

    def test_bool(self):
        true = Value(True)
        false = Value(False)
        self.assertEqual(true, True)
        self.assertEqual(false, False)
        self.assertEqual(true, 1)
        self.assertEqual(false, 0)
        self.assertEqual(int(true), 1)
        self.assertEqual(int(false), 0)
        self.assertEqual(repr(true), "True")
        self.assertEqual(repr(false), "False")

    def test_int(self):
        _123 = Value(123)
        self.assertEqual(_123, 123)
        self.assertEqual(-_123, -123)
        self.assertEqual(int(Value(" 123 xix")), 123)
        self.assertEqual(int(Value(" -123 xix")), -123)
        self.assertEqual(repr(_123), "123")
        self.assertEqual(repr(-_123), "-123")

    def test_float(self):
        _1234 = Value(123.4)
        self.assertEqual(Value(_1234), 123.4)
        self.assertEqual(Value(-_1234), -123.4)
        self.assertEqual(float(Value(" 123.4 xfx")), 123.4)
        self.assertEqual(float(Value(" -123.4 xfx")), -123.4)
        self.assertEqual(repr(_1234), "123.4")
        self.assertEqual(repr(-_1234), "-123.4")


class LogicsTestCase(unittest.TestCase):
    def test(self):
        l = Logics("123")
        res = l.run()
        self.assertEqual(res, 123)
