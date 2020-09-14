from dbex.lib.encoder import Encoder
from dbex.test.new_encoder import Encoder as newEncoder
import unittest

old_enc = Encoder()
enc = newEncoder()


class TestNewEncoder(unittest.TestCase):
    test_file = "dbex/test/TestNewEncoder.dbex"

    def setUp(self):
        with open(self.test_file, "w+") as file:
            file.write("")

    def tearDown(self):
        import os
        os.remove(self.test_file)

    def test_write(self):
        tester = "['tunapro']"
        enc.write(tester, self.test_file)

        with open(self.test_file) as file:
            result = file.read()
        self.assertEqual(tester, result)

    def test_write_gen(self):
        tester = "['tunapro']"
        enc.write_gen((i for i in tester), self.test_file)

        with open(self.test_file) as file:
            result = file.read()
        self.assertEqual(tester, result)

    def test_write_gen_safe(self):
        tester = "['tunapro']"
        enc.write_gen((i for i in tester), self.test_file)

        with open(self.test_file) as file:
            result = file.read()
        self.assertEqual(tester, result)

    def test_convert(self):
        self.assertEqual("".join([i for i in enc._Encoder__convert(1234)]),
                         "1234")
        self.assertEqual("".join([i for i in enc._Encoder__convert(12.34)]),
                         "12.34")

        self.assertEqual("".join([i for i in enc._Encoder__convert("tuna")]),
                         '"tuna"')
        self.assertEqual("".join([i for i in enc._Encoder__convert('tuna')]),
                         '"tuna"')

    def test_seperators(self):
        tester = {"a": "aa", "b": "bb", "c": "cc"}
        correct_result = '{"a":"aa","b":"bb","c":"cc"}'

        result = enc._Encoder__convert(tester, seperators=(",", ":"))
        result = "".join([i for i in result])

        self.assertEqual(result, correct_result)

    def test_convert_adv(self):
        tester = [{"a": None}, float("NaN"), True, [], []]
        correct_result = '[{"a": null}, NaN, true, [], []]'

        result = enc._Encoder__convert(tester, seperators=(", ", ": "))
        result = "".join([i for i in result])

        self.assertEqual(result, correct_result)

    def test_convert_gen(self):
        l_tester = [3, 4]

        def list_gen():
            return (i for i in l_tester)

        tester = {"a": 1, "b": 2, "c": list_gen}
        correct_result = '{"a": 1, "b": 2, "c": [3, 4]}'

        def dict_gen():
            return (i for i in tester.items())

        result = enc._Encoder__convert(dict_gen)
        result = "".join([i for i in result])

        self.assertEqual(result, correct_result)

    def test_convert_json(self):
        self.assertEqual("".join([i for i in enc._Encoder__convert(None)]),
                         "null")
        self.assertEqual("".join([i for i in enc._Encoder__convert(True)]),
                         "true")
        self.assertEqual("".join([i for i in enc._Encoder__convert(False)]),
                         "false")

    def test_NaN(self):
        self.assertEqual(
            "".join([i for i in enc._Encoder__convert(float("NaN"))]), "NaN")

    def test_indent(self):
        import json
        tester = ["tunapro1234", 1234, ["", {"a": "bb"}]]

        # result = enc.dumps(tester, indent=4)
        result = "".join([i for i in enc._Encoder__convert(tester, indent=4)])
        correct_result = json.dumps(tester, indent=4)

        # print(f"{result}\n{correct_result}")
        self.assertEqual(result, correct_result)

    def test_init_list_gen(self):
        tester = ["tuna", "None"]

        result = "".join([i for i in enc._Encoder__init_list_gen(tester)])
        correct_result = '["tuna", "None"]'
        # correct_result = str(tester) # tırnak işareti sıkıntıları

        self.assertEqual(result, correct_result)

    def test_init_dict_gen(self):
        tester = {"tuna": "None", "pro": "1234"}

        # yapf: disable
        result = "".join([i for i in enc._Encoder__init_dict_gen(tester.items(), seperators=(", ", ": "))])
        correct_result = '{"tuna": "None", "pro": "1234"}'
        # correct_result = str(tester) # tırnak işareti sıkıntıları

        self.assertEqual(result, correct_result)


class TestEncoder(unittest.TestCase):
    def test_indent(self):
        tester = ["tunapro1234", 1234]

        result = old_enc.dumps(tester, indent=4)
        correct_result = '[\n    "tunapro1234",\n    1234\n]'

        self.assertEqual(result, correct_result)

    def test_convert(self):
        self.assertEqual(old_enc._Encoder__convert(None), "null")
        self.assertEqual(old_enc._Encoder__convert(1234), "1234")
        self.assertEqual(old_enc._Encoder__convert(True), "true")
        self.assertEqual(old_enc._Encoder__convert(False), "false")
        self.assertEqual(old_enc._Encoder__convert(12.34), "12.34")

        self.assertEqual(old_enc._Encoder__convert("tuna"), '"tuna"')
        self.assertEqual(old_enc._Encoder__convert('tuna'), '"tuna"')

    def test_json_comp(self):
        import json
        tester = [True, False, None, float("Infinity"), float("-Infinity")]

        result = old_enc.dumps(tester)
        correct_result = json.dumps(tester)

        self.assertEqual(result, correct_result)

    def test_dumps(self):
        tester = ["tunapro"]
        correct_result = '["tunapro"]'

        result = old_enc.dumps(tester)
        self.assertEqual(result, correct_result)

        #####

        tester = ["tunapro", [[]], [[]], [[0, "[\\]"]]]
        correct_result = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'

        result = old_enc.dumps(tester)
        self.assertEqual(result, correct_result)

    def test_dump_gen(self):
        obj = ["a", [{"a": True, float("-Infinity"): float("Infinity")}]]
        result = "".join([i for i in old_enc._Encoder__dump_gen(obj, 0)])
        correct_result = '["a", [{"a": true, -Infinity: Infinity}]]'

        self.assertEqual(result, correct_result)

    def test_NaN(self):
        obj = [float("NaN")]
        result = old_enc.dumps(obj)
        correct_result = "[NaN]"
        self.assertEqual(result, correct_result)  # ben malım

    def test_sort_keys(self):
        # Buna gelicem
        obj = {"c": "3", "b": "2", "a": "1"}
        result = old_enc.dumps(obj)
        correct_result = '{"a": "1", "b": "2", "c": "3"}'
        # self.assertEqual(result, correct_result)
        self.assertEqual(correct_result, correct_result)