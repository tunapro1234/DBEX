from dbex.test.new_decoder import Decoder as newDecoder
from dbex.lib.decoder import Decoder
import unittest
# import time
import types


def gen_to_list(gen):
    final = []
    for i in gen:
        if isinstance(i, types.GeneratorType):
            final.append(gen_to_list(i))
        else:
            final.append(i)
    return final


def gen_to_dict(gen):
    final = {}
    for key, value in gen:
        if isinstance(value, types.GeneratorType):
            final[key] = gen_to_dict(value)
        else:
            final[key] = value
    return final


def gen_normalizer(gen_func):
    gen = gen_func()
    final = None  # pylint hata veriyor
    if gen_func.__name__ == "dict_gen":
        final = {}
        for key, value in gen:
            if callable(value):
                final[key] = gen_normalizer(value)
            else:
                final[key] = value

    elif gen_func.__name__ == "list_gen":
        final = []
        for value in gen:
            if callable(value):
                final.append(gen_normalizer(value))
            else:
                final.append(value)

    return final


old_dec = Decoder()
dec = newDecoder()


class TestNewDecoder(unittest.TestCase):
    test_file = "dbex/test/TestNewDecoder.dbex"

    def setUp(self):
        with open(self.test_file, "w+") as file:
            file.write("")

    def tearDown(self):
        import os
        os.remove(self.test_file)

    def test_read(self):
        tester = "['tunapro']"
        with open(self.test_file, "w+") as file:
            file.write(tester)

        result = dec.read(self.test_file)
        self.assertEqual(tester, result)

    def test_read_gen(self):
        tester = "['tunapro']"
        with open(self.test_file, "w+") as file:
            file.write(tester)

        result = "".join([i for i in dec.read_gen(self.test_file)])
        self.assertEqual(tester, result)

    def test_read_gen_safe(self):
        tester = "['tunapro']"
        with open(self.test_file, "w+") as file:
            file.write(tester)

        result = "".join([i for i in dec.read_gen_safe(self.test_file)])
        self.assertEqual(tester, result)

    def test_convert_adv(self):
        tester = '[{"a": None}, NaN, true, [], []]'
        correct_result = [{"a": None}, float("NaN"), True, [], []]

        result = dec.gen_normalizer(dec._Decoder__convert(tester))

        self.assertEqual(result, correct_result)

    def test_convert_gen(self):
        correct_result = {"a": 1, "b": 2, "c": [3, 4]}
        tester = '{"a": 1, "b": 2, "c": [3, 4]}'

        result = dec.gen_normalizer(dec._Decoder__convert(tester))

        self.assertEqual(result, correct_result)


class TestDecoder(unittest.TestCase):
    def test_gen_normalizer_dict(self):
        def dict_gen():
            return (i for i in {"t": "tt"}.items())

        tester = {"a": "aa", "b": "bb", "gen": dict_gen}

        def dict_gen():
            return (i for i in tester.items())

        result = old_dec.gen_normalizer(dict_gen)

        correct_result = {"a": "aa", "b": "bb", "gen": {"t": "tt"}}

        self.assertEqual(result, correct_result)

    def test_gen_normalizer_list(self):
        def list_gen():
            return (i for i in [0, 1])

        tester = [0, 1, 2, 3, 4, list_gen]

        def list_gen():
            return (i for i in tester)

        result = old_dec.gen_normalizer(list_gen)
        correct_result = [0, 1, 2, 3, 4, [0, 1]]
        self.assertEqual(result, correct_result)

    def test_tokenize(self):
        tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
        correct_result = [
            '[', '"', 'tunapro', '"', ',', ' ', '[', '[', ']', ']', ',', ' ',
            '[', '[', ']', ']', ',', ' ', '[', '[', '0', ',', ' ', '"', '[',
            '\\', ']', '"', ']', ']', ']'
        ]

        result = gen_to_list(old_dec._Decoder__tokenize(tester))
        self.assertEqual(result, correct_result)

        result = gen_to_list(old_dec._Decoder__tokenize((i for i in tester)))
        self.assertEqual(result, correct_result)

    def test_json_comp(self):
        import json
        tester = '[true, false, null, Infinity, -Infinity]'

        result = old_dec.loads(tester)
        correct_result = json.loads(tester)

        self.assertEqual(result, correct_result)

    def test_NaN(self):
        result = old_dec.loads("NaN")
        self.assertNotEqual(result, result)

    def test_loads(self):
        tester = '["tunapro", (()), [[]], [[0, "[\\]"]]]'
        correct_result = ["tunapro", ((), ), [[]], [[0, "[\\]"]]]
        # correct_result = ['"tunapro"', [[]], [[]], [[0, '"[\\]"']]]

        result = old_dec.loads(tester)
        self.assertEqual(result, correct_result)

    def test_load__(self):
        # yapf: disable
        tester = '[', '"tunapro"', ',', '(', '(', ')', ',', ')', ',', '[', '[', ']', ']', ',', '[', '[', '0', ']', ']', ']'
        correct_result = ["tunapro", ((), ), [[]], [[0]]]
        generator_func = lambda: (i for i in tester)

        result = old_dec._Decoder__load(generator_func, max_depth=0)
        self.assertEqual(result, correct_result)

    def test_load(self):
        tester = "['tunapro', (()), [[]], [[0, '[\\]']], None]"
        correct_result = ["tunapro", ((), ), [[]], [[0, "[\\]"]], None]

        path = "dbex/test/test.dbex"
        with open(path, "w+") as file:
            file.write(tester)

        result = old_dec.load(path)
        self.assertEqual(result, correct_result)

    def test_tokenize_gen(self):
        tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
        correct_result = [
            '[', '"tunapro"', ',', '[', '[', ']', ']', ',', '[', '[', ']', ']',
            ',', '[', '[', '0', ',', '"[\\]"', ']', ']', ']'
        ]

        result = old_dec._Decoder__tokenize_gen(tester)
        if isinstance(result, types.GeneratorType):
            result = gen_to_list(result)

        self.assertEqual(result, correct_result)

    def test_read_gen(self):
        path = "dbex/test/test.dbex"
        with open(path, "w+", encoding="utf-8") as file:
            correct_result = file.read()

        result = "".join([i for i in old_dec.read_gen(path)])
        self.assertEqual(result, correct_result)

        if not isinstance(old_dec.read_gen(path), types.GeneratorType):
            # Haha
            self.assertEqual(False, True)

    def test_convert(self):
        self.assertEqual(old_dec._Decoder__convert("None"), None)
        self.assertEqual(old_dec._Decoder__convert("1234"), 1234)
        self.assertEqual(old_dec._Decoder__convert("True"), True)
        self.assertEqual(old_dec._Decoder__convert("False"), False)
        self.assertEqual(old_dec._Decoder__convert("12.34"), 12.34)

        self.assertEqual(old_dec._Decoder__convert("null"), None)
        self.assertEqual(old_dec._Decoder__convert("true"), True)
        self.assertEqual(old_dec._Decoder__convert("false"), False)

        self.assertEqual(old_dec._Decoder__convert('"Tunapro1234"'), "Tunapro1234")
        self.assertEqual(old_dec._Decoder__convert("'Tunapro1234'"), "Tunapro1234")

    def test_init_dict_gen(self):
        with self.assertRaises(Exception):
            # ::
            tester = [
                "{", "'a'", ":", "'aa'", ":", "'aa'", ",", "'b'", ":", "'bb'",
                "}"
            ]

            result = old_dec._Decoder__init_dict_gen(lambda:
                                                (i for i in tester[1:]))
            result = gen_normalizer(result)
        ###
        with self.assertRaises(Exception):
            # virgülsüz
            tester = ["{", "'a'", ":", "'aa'", "'b'", ":", "'bb'", "}"]

            result = old_dec._Decoder__init_dict_gen(lambda:
                                                (i for i in tester[1:]))
            result = gen_normalizer(result)
        ###
        # yapf: disable
        tester = [ "{",
                        "'a'", ":", "'aa'", ",",
                        "None", ":", "'none'", ",",
                        "\"True\"", ":", "'true'", ",",
                        "0.3", ":", "'0.3'", ",",
                        "True", ":", "'true'", ",",
                        "(", ")", ":", "False", # YARIN BURAYA Bİ GÖZ AT
                    "}" ]

        correct_result = {'a':'aa', None:'none', "True":'true', 0.3:'0.3', True:'true', ():False}
        def dict_gen():
            return old_dec._Decoder__init_dict_gen(lambda: (i for i in tester[1:]))
        result = gen_normalizer(dict_gen)
        self.assertEqual(result, correct_result)


    def test_init_dict_gen_recur(self):
        tester = [ "{",
                        "'gen'", ":", "{", "'b'", ":", "'bb'", "}", ",",
                        "'gen2'", ":", "{", "(", ")", ":", "{", "}", "}",
                    "}" ]

        correct_result = {'gen': {'b': 'bb'}, 'gen2': {(): {}}}

        def dict_gen():
            return old_dec._Decoder__init_dict_gen(lambda: (i for i in tester[1:]))
        result = gen_normalizer(dict_gen)

        self.assertEqual(result, correct_result)

    # def test_sort_keys(self):


    def test_header(self):
        self.assertEqual(1, 1)
