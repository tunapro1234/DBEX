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
    test_file = "test_init.json"

    def test_load(self):
        correct_result = [12, 34]
        with open(self.test_file, "w+") as file:
            file.write(str(correct_result))

        result = dec.load(self.test_file)
        self.assertEqual(result, correct_result)

        os.remove(self.test_file)

    def test_loads(self):
        result = dec.loads("[]")
        correct_result = []
        self.assertEqual(result, correct_result)

    def test_loader(self):
        correct_result = ["tuna", "pro", "12", "34"]
        with open(self.test_file, "w+") as file:
            file.write(str(correct_result))

        result = gen_normalize(dec.loader(self.test_file))
        self.assertEqual(result, correct_result)

        os.remove(self.test_file)

    ##########################################################

    def test_dump(self):
        tester = ["tunapro1234"]
        enc.dump(tester, self.test_file, indent=0)
        correct_result = str(tester)
        
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
        tester = ["tuna", "pro", "12", "34"]
        enc.dumper(tester, path=self.test_file, indent=0)
        correct_result = str(tester)
        
        with open(self.test_file, "r") as file:
            result = file.read()
            
        self.assertEqual(result, correct_result)

        os.remove(self.test_file)
