from dbex.__init__ import DebugEncrypter
from dbex.__init__ import Decoder  # sonunda
from dbex.__init__ import Encoder
import unittest
import os


def gen_normalize(gen_func, *args, **kwargs):
    gen = gen_func()
    if gen_func.__name__ == "dict_gen":
        final = {}
        for key, value in gen:
            if callable(value):
                final[key] = gen_normalize(value)
            else:
                final[key] = value

    elif gen_func.__name__ in ["list_gen", "tuple_gen"]:
        final = []
        for value in gen:
            if callable(value):
                final.append(gen_normalize(value))
            else:
                final.append(value)

    return final


def _print_gen(gen_func, *args, **kwargs):
    gen = gen_func()
    if gen_func.__name__ == "dict_gen":
        final = {}
        for key, value in gen:
            if callable(value):
                final[key] = gen_normalize(value)
            else:
                final[key] = value

    elif gen_func.__name__ in ["list_gen", "tuple_gen"]:
        final = []
        for value in gen:
            if callable(value):
                final.append(gen_normalize(value))
            else:
                final.append(value)

    return final


dec = Decoder()
enc = Encoder()


class TestMainPackage(unittest.TestCase):
    test_file = "dbex/test/test_init.json"

    def setUp(self):
        with open(self.test_file, "w+") as file:
            file.write("")

    def tearDown(self):
        os.remove(self.test_file)

    def test_load(self):
        correct_result = [12, 34]
        with open(self.test_file, "w+") as file:
            file.write(str(correct_result))

        result = dec.load(self.test_file)
        self.assertEqual(result, correct_result)

        os.remove(self.test_file)

    def test_loads(self):
        result = dec.loads("{12:23,34:45}")
        correct_result = {12: 23, 34: 45}
        self.assertEqual(result, correct_result)

    def test_loader(self):
        correct_result = ["tuna", "pro", "12", "34"]
        with open(self.test_file, "w+") as file:
            file.write(str(correct_result))

        result = dec.gen_normalizer(dec.loader(path=self.test_file))
        self.assertEqual(result, correct_result)

        os.remove(self.test_file)

    ##########################################################

    def test_dump(self):
        import json
        tester = ["tunapro1234"]
        enc.dump(tester, path=self.test_file, indent=0)
        correct_result = json.dumps(tester)

        with open(self.test_file, "r") as file:
            result = file.read()

        self.assertEqual(result, correct_result)

        os.remove(self.test_file)

    def test_dumps(self):
        tester = []
        result = enc.dumps(tester)
        correct_result = str(tester)
        self.assertEqual(result, correct_result)

    def test_dumper(self):
        import json
        tester = ["tuna", "pro", "12", "34"]
        enc.dumper(tester, path=self.test_file, indent=0)
        correct_result = json.dumps(tester)

        with open(self.test_file, "r") as file:
            result = file.read()

        self.assertEqual(result, correct_result)

        os.remove(self.test_file)

    ##########################################################

    def test_dumps_loads(self):
        tester = "{12: 23, 34: 45}"

        result = enc.dumps(dec.loads(tester))
        result2 = enc.dumps(dec.loads(tester, max_depth="all"))

        self.assertEqual(tester, result)
        self.assertEqual(tester, result2)
        # print(f"{tester}\n{result}\n{result2}")

    def test_loads_dumps(self):
        tester = {12: 23, 34: 45}

        result = dec.loads(enc.dumps(tester))
        self.assertEqual(tester, result)

    def test_loads_dumps2(self):
        tester = {12: 23, 34: 45}

        result2 = dec.loads(lambda: enc.dumps(tester, max_depth="all"))
        self.assertEqual(tester, result2)
        # print(f"{tester}\n{result}\n{result2}")

    def test_dumps_loads(self):
        tester = '["json bunu yapabilir mi?", "tunapro", [[]]]'

        result = enc.dumps(dec.loads(tester))
        result2 = enc.dumps(dec.loads(tester, max_depth="all"))

        self.assertEqual(tester, result)
        self.assertEqual(tester, result2)
        print(f"{tester}\n{result}\n{result2}")
