from dbex.lib.encoder import Encoder
import unittest

enc = Encoder()


class TestEncoder(unittest.TestCase):
    def test_indent(self):
        tester = ["tunapro1234", 1234]
        
        result = enc.dumps(tester, indent=4)
        correct_result = '[\n    "tunapro1234",\n    1234\n]'
        
        self.assertEqual(result, correct_result)
    
    def test_convert(self):
        self.assertEqual(enc._Encoder__convert(None), "null")
        self.assertEqual(enc._Encoder__convert(1234), "1234")
        self.assertEqual(enc._Encoder__convert(True), "true")
        self.assertEqual(enc._Encoder__convert(False), "false")
        self.assertEqual(enc._Encoder__convert(12.34), "12.34")

        self.assertEqual(enc._Encoder__convert("Tunapro1234"), '"Tunapro1234"')
        self.assertEqual(enc._Encoder__convert('Tunapro1234'), '"Tunapro1234"')

    def test_json_comp(self):
        import json
        tester = [True, False, None, float("Infinity"), float("-Infinity")]

        result = enc.dumps(tester)
        correct_result = json.dumps(tester)

        self.assertEqual(result, correct_result)

    def test_dumps(self):
        tester = ["tunapro"]
        correct_result = '["tunapro"]'

        result = enc.dumps(tester)
        self.assertEqual(result, correct_result)

        #####

        tester = ["tunapro", [[]], [[]], [[0, "[\\]"]]]
        correct_result = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'

        result = enc.dumps(tester)
        self.assertEqual(result, correct_result)

    def test_dump_gen(self):
        obj = ["a", [{"a": True, float("-Infinity"): float("Infinity")}]]
        result = "".join([i for i in enc._Encoder__dump_gen(obj, 0)])
        correct_result = '["a", [{"a": true, -Infinity: Infinity}]]'

        self.assertEqual(result, correct_result)

    def test_NaN(self):
        obj = [float("NaN")]
        result = enc.dumps(obj)
        correct_result = "[NaN]"
        self.assertEqual(result, correct_result)  # ben malım

    def test_sort_keys(self):
        # Buna gelicem
        obj = {"c": "3", "b": "2", "a": "1"}
        result = enc.dumps(obj)
        correct_result = '{"a": "1", "b": "2", "c": "3"}'
        # self.assertEqual(result, correct_result)
        self.assertEqual(correct_result, correct_result)