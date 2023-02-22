import unittest, logics

class LogicsTestCase(unittest.TestCase):
    def test(self):
        l = logics.Logics("123")
        res = l.run()
        self.assertEqual(res, 123)
