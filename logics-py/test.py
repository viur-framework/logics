from logics import Logics, Value
import unittest


class ValueTestCase(unittest.TestCase):
    def test_none(self):
        none = Value(None)
        self.assertEqual(none, None)
        self.assertEqual(bool(none), False)
        self.assertEqual(int(none), 0)
        self.assertEqual(float(none), 0.0)

    def test_bool(self):
        true = Value(True)
        false = Value(False)
        self.assertEqual(true, True)
        self.assertEqual(false, False)
        self.assertEqual(true, 1)
        self.assertEqual(false, 0)
        self.assertEqual(int(true), 1)
        self.assertEqual(int(false), 0)

    def test_int(self):
        self.assertEqual(Value(123), 123)
        self.assertEqual(Value(-123), -123)
        self.assertEqual(int(Value(" 123 xix")), 123)
        self.assertEqual(int(Value(" -123 xix")), -123)

    def test_float(self):
        self.assertEqual(Value(123.4), 123.4)
        self.assertEqual(Value(-123.4), -123.4)
        self.assertEqual(float(Value(" 123.4 xfx")), 123.4)
        self.assertEqual(float(Value(" -123.4 xfx")), -123.4)


class LogicsTestCase(unittest.TestCase):
    def test(self):
        l = Logics("123")
        res = l.run()
        self.assertEqual(res, 123)
