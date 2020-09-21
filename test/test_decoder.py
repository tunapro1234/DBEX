from dbex.lib.decoder import Decoder
from dbex.lib.decoder import DBEXDecodeError
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


dec = Decoder()


class TestDecoder(unittest.TestCase):
	test_file = "dbex/test/TestNewDecoder.dbex"

	def setUp(self):
		with open(self.test_file, "w+") as file:
			file.write("")

	def tearDown(self):
		import os
		os.remove(self.test_file)

##### COMPABILITY

	def test_json_comp(self):
		import json
		tester = '[true, false, null, Infinity, -Infinity]'

		# result = dec.loads(tester)
		result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(tester))
		correct_result = json.loads(tester)

		self.assertEqual(result, correct_result)

	def test_NaN(self):
		tester = "NaN"
		# result = dec.loads("NaN")
		result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(tester))
		self.assertNotEqual(result, result)

##### TOKENIZERS

	def test_tokenize(self):
		tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
		correct_result = [
			'[', '"', 'tunapro', '"', ',', ' ', '[', '[', ']', ']', ',', ' ',
			'[', '[', ']', ']', ',', ' ', '[', '[', '0', ',', ' ', '"', '[',
			'\\', ']', '"', ']', ']', ']'
		]

		result = gen_to_list(dec._Decoder__tokenize(tester))
		self.assertEqual(result, correct_result)

		result = gen_to_list(dec._Decoder__tokenize((i for i in tester)))
		self.assertEqual(result, correct_result)

	def test_tokenize_control(self):
		tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
		correct_result = [
		 '[', '"tunapro"', ',', '[', '[', ']', ']', ',', '[', '[', ']', ']',
		 ',', '[', '[', '0', ',', '"[\\]"', ']', ']', ']'
		]

		result = dec._Decoder__tokenize_control(tester)
		if isinstance(result, types.GeneratorType):
			result = gen_to_list(result)

		self.assertEqual(result, correct_result)

##### GEN NORMALIZER
	def test_gen_normalizer_dict(self):
		def dict_gen():
			return (i for i in {"t": "tt"}.items())

		tester = {"a": "aa", "b": "bb", "gen": dict_gen}

		def dict_gen():
			return (i for i in tester.items())

		result = dec.gen_normalizer(dict_gen)

		correct_result = {"a": "aa", "b": "bb", "gen": {"t": "tt"}}

		self.assertEqual(result, correct_result)

	def test_gen_normalizer_list(self):
		def list_gen():
			return (i for i in [0, 1])

		tester = [0, 1, 2, 3, 4, list_gen]

		def list_gen():
			return (i for i in tester)

		result = dec.gen_normalizer(list_gen)
		correct_result = [0, 1, 2, 3, 4, [0, 1]]
		self.assertEqual(result, correct_result)

##### TEST LOAD...

	def test_load(self):
		correct_result = ["tunapro", ((), ), [[]], [[0, "[\\]"]], None]
		tester = str(correct_result)
		
		with open(self.test_file, "w+") as file:
			file.write(tester)

		result = dec.load(path=self.test_file)
		self.assertEqual(result, correct_result)

	def test_loads(self):
		correct_result = ["tunapro", ((), ), [[]], [[0, "[\\]"]]]
		# correct_result = ['"tunapro"', [[]], [[]], [[0, '"[\\]"']]]
		tester = str(correct_result)
		
		result = dec.loads(tester)
		self.assertEqual(result, correct_result)

###### CONVERT DICT

	def test_convert_dict_1(self):
		correct_result = {'a':'aa', 'b':'bb', 'c':'cc'}
		result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(str(correct_result)))
		
		self.assertEqual(result, correct_result)

	def test_convert_dict_2(self):
		with self.assertRaises(DBEXDecodeError):
			# yapf: disable
			tester = [
			 "{", 
			 	"'a'", ":", "'aa'", 
				 ":", "'aa'", ",", 
				 "'b'", ":", "'bb'", 
			 "}"]
			
			result = dec._Decoder__convert(lambda: (i for i in tester))
			# yapf: enable
		###
		with self.assertRaises(DBEXDecodeError):
			# virgülsüz
			tester = ["{", "'a'", ":", "'aa'", "'b'", ":", "'bb'", "}"]

			# yapf: disable
			result = dec._Decoder__convert(lambda: (i for i in tester))
		###
		# yapf: disable
		# tester = [ "{",
		# 	"'a'", ":", "'aa'", ",",
		# 	"None", ":", "'none'", ",",
		# 	"\"True\"", ":", "'true'", ",",
		# 	"0.3", ":", "'0.3'", ",",
		# 	"True", ":", "'true'", ",",
		# 	"(", ")", ":", "False", 
		#    "}" ]

		# correct_result = {'a':'aa', None:'none', "True":'true', 0.3:'0.3', True:'true', ():False}
		# result = dec._Decoder__convert(dec._Decoder__tokenize_control(str(correct_result)))
		# self.assertEqual(result, correct_result)

	def test_convert_dict_recur(self):
		correct_result = {"a": 1, "b": 2, "c": {"3": 4}}
		tester = '{"a": 1, "b": 2, "c": {"3": 4}}'
		result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(tester))
		self.assertEqual(result, correct_result)

	def test_convert_dict_recur_2(self):
		correct_result = {"gen2":{():{}}}
		tester = str(correct_result)

		result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(tester))

		self.assertEqual(result, correct_result)

###### CONVERT OBJ

	def test_convert_obj(self):
		self.assertEqual(dec._Decoder__convert_obj("None"), None)
		self.assertEqual(dec._Decoder__convert_obj("1234"), 1234)
		self.assertEqual(dec._Decoder__convert_obj("True"), True)
		self.assertEqual(dec._Decoder__convert_obj("False"), False)
		self.assertEqual(dec._Decoder__convert_obj("12.34"), 12.34)

		self.assertEqual(dec._Decoder__convert_obj('"Tunapro1234"'), "Tunapro1234")
		self.assertEqual(dec._Decoder__convert_obj("'Tunapro1234'"), "Tunapro1234")

	def test_convert_obj_json_comp(self):
		self.assertEqual(dec._Decoder__convert_obj("null"), None)
		self.assertEqual(dec._Decoder__convert_obj("true"), True)
		self.assertEqual(dec._Decoder__convert_obj("false"), False)

##### CONVERT LIST 

	def test_convert_list(self):
		tester = '["false", True, [1, 2, 3, []]]'
		correct_result = ["false", True, [1, 2, 3, []]]

		result = dec.loads(tester)
		# result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(tester))

		self.assertEqual(result, correct_result)
	
	def test_convert_tuple(self):
		correct_result = ("false", True, (1, 2, 3, ()))
		tester = str(correct_result)
		result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(tester))

		self.assertEqual(result, correct_result)
		
		correct_result = [(), True]
		tester = str(correct_result)
		result = dec._Decoder__convert(lambda: dec._Decoder__tokenize_control(tester))

		self.assertEqual(result, correct_result)

##### READ 

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
		
		if not isinstance(dec.read_gen(self.test_file), types.GeneratorType):
			self.assertEqual(False, True)
			# Haha

	def test_read_gen_safe(self):
		tester = "['tunapro']"
		with open(self.test_file, "w+") as file:
			file.write(tester)

		result = "".join([i for i in dec.read_gen_safe(self.test_file)])
		self.assertEqual(tester, result)
