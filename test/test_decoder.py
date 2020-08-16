import dbex.lib.decoder as db
import unittest
import types
import time


def gen_to_list(gen):
    final = []
    for i in gen:
        if isinstance(i, types.GeneratorType):
            final.append(gen_to_list(i))
        else:
            final.append(i)
    return final

# tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
def gen_func(gen=range(6)):
    for i in gen:
        if i == 5:
            yield gen_func(range(2))
        else:
            yield i


class TestDecoder(unittest.TestCase):
    def test_tokenize(self):
        tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
        correct_result = ['[', '"', 'tunapro', '"', ',', ' ', '[', '[', ']', ']', ',', ' ', '[', '[', ']', ']', ',', ' ', '[', '[', '0', ',', ' ', '"', '[', '\\', ']', '"', ']', ']', ']']
        
        result = gen_to_list(db.tokenize_(tester))
        self.assertEqual(result, correct_result)

        result = gen_to_list(db.tokenize_((i for i in tester)))
        self.assertEqual(result, correct_result)

    def test_gen_to_list(self):
        correct_result = [0, 1, 2, 3, 4, [0, 1]]
    
        result = db.gen_to_list(gen_func())
        correct_result = gen_to_list(gen_func())
        self.assertEqual(result, correct_result)

    def test_loads(self):
        tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
        correct_result = ["tunapro", [[]], [[]], [[0, "[\\]"]]]
        
        result = db.loads(tester, is_generator=0)
        self.assertEqual(result, correct_result)

        result = db.loads((i for i in tester), is_generator=0)
        self.assertEqual(result, correct_result)
        
    def test_tokenize_gen(self):
        tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
        correct_result = ['[', '"tunapro"', ',', ' ', '[', '[', ']', ']', ',', ' ', '[', '[', ']', ']', ',', ' ', '[', '[', '0', ',', ' ', '"[\\]"', ']', ']', ']']
        
        result = db.tokenize_gen(tester)
        if isinstance(result, types.GeneratorType):
            result = gen_to_list(result)

        self.assertEqual(result, correct_result)

    def test_read_file_gen(self):
        path = "dbex/res/test.dbex"
        with open(path, "w+", encoding="utf-8") as file:
            correct_result = file.read()
        
        result = "".join([i for i in db.read_file_gen(path)])
        self.assertEqual(result, correct_result)
        
        if not isinstance(db.read_file_gen(path), types.GeneratorType):
            # Haha
            self.assertEqual(False, True)