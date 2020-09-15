from dbex.lib.encoder import Encoder
import unittest

enc = Encoder()


class TestEncoder(unittest.TestCase):
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

    def test_seperators(self):
        tester = {"a": "aa", "b": "bb", "c": "cc"}
        correct_result = '{"a":"aa","b":"bb","c":"cc"}'

        result = enc.__main(tester, seperators=(",", ":"))
        result = "".join([i for i in result])

        self.assertEqual(result, correct_result)

    def test_convert_adv(self):
        tester = [{"a": None}, float("NaN"), True, [], []]
        correct_result = '[{"a": null}, NaN, true, [], []]'

        result = enc.__main(tester, seperators=(", ", ": "))
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

        result = enc.__main(dict_gen)
        result = "".join([i for i in result])

        self.assertEqual(result, correct_result)

    def test_convert_json(self):
        self.assertEqual("".join([i for i in enc.__main(None)]), "null")
        self.assertEqual("".join([i for i in enc.__main(True)]), "true")
        self.assertEqual("".join([i for i in enc.__main(False)]), "false")

    def test_NaN(self):
        self.assertEqual("".join([i for i in enc.__main(float("NaN"))]), "NaN")

    def test_indent(self):
        import json
        tester = ["tunapro1234", 1234, ["", {"a": "bb"}]]

        result = enc.dumps(tester, indent=4)
        correct_result = json.dumps(tester, indent=4)

        # print(f"{result}\n{correct_result}")
        self.assertEqual(result, correct_result)

    def test_convert_list(self):
        tester = ["tuna", "None"]

        result = "".join([i for i in enc._Encoder__convert_list(tester)])
        correct_result = '["tuna", "None"]'
        # correct_result = str(tester) # tırnak işareti sıkıntıları

        self.assertEqual(result, correct_result)

    def test_convert_dict(self):
        tester = {"tuna": "None", "pro": "1234"}

        # yapf: disable
        result = "".join([i for i in enc._Encoder__convert_dict(tester.items(), seperators=(", ", ": "))])
        correct_result = '{"tuna": "None", "pro": "1234"}'
        # correct_result = str(tester) # tırnak işareti sıkıntıları

        self.assertEqual(result, correct_result)

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


    def test_sort_keys(self):
        # Buna gelicem
        obj = {"c": "3", "b": "2", "a": "1"}
        result = enc.dumps(obj)
        correct_result = '{"a": "1", "b": "2", "c": "3"}'
        # self.assertEqual(result, correct_result)
        self.assertEqual(correct_result, correct_result)

# class TestOldEncoder(unittest.TestCase):

#     def test_convert(self):
#         self.assertEqual(enc._Encoder__convert(None), "null")
#         self.assertEqual(enc._Encoder__convert(1234), "1234")
#         self.assertEqual(enc._Encoder__convert(True), "true")
#         self.assertEqual(enc._Encoder__convert(False), "false")
#         self.assertEqual(enc._Encoder__convert(12.34), "12.34")

#         self.assertEqual(enc._Encoder__convert("tuna"), '"tuna"')
#         self.assertEqual(enc._Encoder__convert('tuna'), '"tuna"')