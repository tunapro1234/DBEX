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

def gen_to_dict(gen):
    final = {}
    for key, value in gen:
        if isinstance(value, types.GeneratorType):
            final[key] = gen_to_dict(value)
        else:
            final[key] = value
    return final

# tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
def gen_func(gen=range(6)):
    for i in gen:
        if i == 5:
            yield gen_func(range(2))
        else:
            yield i

def gen_normalize(gen_func):
    gen = gen_func()
    if gen_func.__name__ == "dict_gen":
        final = {}
        for key, value in gen:
            if callable(value):
                final[key] = gen_normalize(value)
            else:
                final[key] = value

    elif gen_func.__name__ == "list_gen":
        final = []
        for value in gen:
            if callable(value):
                final.append(gen_normalize(value))
            else:
                final.append(value)
    
    return final



class TestDecoder(unittest.TestCase):
    
    def test_gen_to_dict(self):
        tester_ = {"t":"tt"} 
        gen = (i for i in tester_.items())
        tester = {"a":"aa", "b":"bb", "gen":gen}
        result = db.gen_to_dict((i for i in tester.items()))
        
        correct_result = {"a":"aa", "b":"bb", "gen":{"t":"tt"}}
        
        self.assertEqual(result, correct_result)
    
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

    # Çok hata çıkarıyor
    # def test_json_comp(self):
    #     import json
    #     tester = '[true, false, null, Infinity, -Infinity, NaN]'
        
    #     result = db.loads(tester, is_generator=0)
    #     correct_result = json.loads(tester)
        
    #     self.assertEqual(result, correct_result)
        

    def test_loads(self):
        tester = '["tunapro", (()), [[]], [[0, "[\\]"]]]'
        correct_result = ["tunapro", ((), ), [[]], [[0, "[\\]"]]]
        # correct_result = ['"tunapro"', [[]], [[]], [[0, '"[\\]"']]]
        
        result = db.loads(tester, is_generator=0)
        self.assertEqual(result, correct_result)

        # result = db.loads((i for i in tester), is_generator=0)
        # self.assertEqual(result, correct_result)
        
    def test_loads_adv(self):
        tester = "['tunapro', (()), [[]], [[0, '[\\]']], None]"
        correct_result = ["tunapro", ((),), [[]], [[0, "[\\]"]], None]
        
        # result = db.loads(tester, is_generator=0)
        # self.assertEqual(result, correct_result)

        result = db.loads((i for i in tester), is_generator=0)
        self.assertEqual(result, correct_result)
        
    def test_tokenize_gen(self):
        tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
        correct_result = ['[', '"tunapro"', ',', '[', '[', ']', ']', ',', '[', '[', ']', ']', ',', '[', '[', '0', ',', '"[\\]"', ']', ']', ']']
        
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
    
    
    def test_convert_(self):
        self.assertEqual(db.convert_("None"), None)
        self.assertEqual(db.convert_("1234"), 1234)
        self.assertEqual(db.convert_("True"), True)
        self.assertEqual(db.convert_("False"), False)
        self.assertEqual(db.convert_("12.34"), 12.34)
        
        self.assertEqual(db.convert_("null"), None)
        self.assertEqual(db.convert_("true"), True)
        self.assertEqual(db.convert_("false"), False)
        
        self.assertEqual(db.convert_('"Tunapro1234"'), "Tunapro1234")
        self.assertEqual(db.convert_("'Tunapro1234'"), "Tunapro1234")
        

    def test_init_dict_gen(self):
        with self.assertRaises(Exception):
            # ::
            tester = [ "{", 
                            "'a'", ":", "'aa'", ":", "'aa'", ",",
                            "'b'", ":", "'bb'",
                        "}" ]
            
            result = db.init_dict_gen(lambda: (i for i in tester[1:]))
            result = gen_normalize(result)
        ###
        with self.assertRaises(Exception):
            # virgülsüz
            tester = [ "{", 
                            "'a'", ":", "'aa'",
                            "'b'", ":", "'bb'",
                        "}" ]
            
            result = db.init_dict_gen(lambda: (i for i in tester[1:]))
            result = gen_normalize(result)
        ###

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
            return db.init_dict_gen(lambda: (i for i in tester[1:]))
        result = gen_normalize(dict_gen)
        self.assertEqual(result, correct_result)
        

    def test_init_dict_gen_recur(self):
        tester = [ "{", 
                        "'gen'", ":", "{", "'b'", ":", "'bb'", "}", ",", 
                        "'gen2'", ":", "{", "(", ")", ":", "{", "}", "}",
                    "}" ]
        
        correct_result = {'gen': {'b': 'bb'}, 'gen2': {(): {}}}

        def dict_gen():
            return db.init_dict_gen(lambda: (i for i in tester[1:]))
        result = gen_normalize(dict_gen)

        self.assertEqual(result, correct_result)
        

        