import dbex.lib.encoder as db
import unittest

class TestEncoder(unittest.TestCase):
    def test_dumps(self):
        tester = ["tunapro", [[]], [[]], [[0, "[\\]"]]]
        correct_result = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
        
        result = db.dumps(tester)
        self.assertEqual(result, correct_result)
        
    def test_dump_gen(self):
        obj = ["a", [{"a":float("NaN"), float("-Infinity"):float("Infinity")}]]
        result = "".join([i for i in db.dump_gen(obj, 0)])
        correct_result = '["a", [{"a":NaN, -Infinity:Infinity}]]'
        
        self.assertEqual(result, correct_result)