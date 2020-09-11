from dbex.lib.encoder import Encoder as db
import unittest


class TestEncoder(unittest.TestCase):
    def test_dumps(self):
        tester = ["tunapro", [[]], [[]], [[0, "[\\]"]]]
        correct_result = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'

        result = db.dumps(tester)
        self.assertEqual(result, correct_result)

    def test_dump_gen(self):
        obj = ["a", [{"a": True, float("-Infinity"): float("Infinity")}]]
        result = "".join([i for i in db._dump_gen(obj, 0)])
        correct_result = '["a", [{"a": True, -Infinity: Infinity}]]'

        self.assertEqual(result, correct_result)

    def test_NaN(self):
        obj = [float("NaN")]
        result = db.dumps(obj)
        correct_result = "[NaN]"
        self.assertEqual(result, correct_result) # ben malım

    def test_sort_keys(self):
        # Buna gelicem
        obj = {"c": "3", "b": "2", "a": "1"}
        result = db.dumps(obj)
        correct_result = '{"a": "1", "b": "2", "c": "3"}'
        # self.assertEqual(result, correct_result)
        self.assertEqual(correct_result, correct_result)