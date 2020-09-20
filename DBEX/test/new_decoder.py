"""
Evveettt dün 10 saat uğraşıp baştan yazdığım encoder classına yaptığım geliştirmeyi decoder classına da yapma zamanı geldi
sonra köle gibi yorumlamam gerekiyor
sonra encryptor 
sonra header
pff çok iş var


planım neredeyse new_encoder ile aynı olacak 
__convert ->    __router ->     __convert_list | -> __convert
						|->     __convert_dict |

__find_next_closing, gen_normalizer ve read şeyleri de lazım

__convert ve altındaki tüm fonksiyonlar generator olacak
şu anki decoderdaki tokenize ve tokenize_gen muhtemelen aynı kalır

Burada küçük bir planlama hatası yapmışım __convert __convert_obj ve __router 
generator olmayacak, __router generator function döndürdüğü için convert de normal olabiliyor


gen_normalizer ile çevirme load... fonksiyonlarında yapılacak

	convert generator döndüren fonksiyon alıyor onu routera atıyor router 
içinde generator kısıtlanıp fonksiyonla wrapplanip convert_listlere filan gönderiliyor

ama convert objeleri nasıl dönecek
__convert(lambda: (__tokenize_gen(__tokenize(string or generator))))
normalde __load ilk elemana bakıp yolluyordu biz de o tarz bir şey yapabilirz
__convert yerine __main yapsam main içinden __converte atsa daha hoş olur

düznlenmiş hali:
gen_normalizer(__convert(__tokenize_control(__tokenize(read_gen()))))
tabii tokenize_control fonksiyonu kendi içinde __tokenize fonksiyonunu çağırıyorr o yüzden çağırmam gerek yoktu

__convert_obj yaptım
hadi başlayalım
"""

# from dbex.lib.encryption import decrypter
import dbex.res.globalv as gvars
# import types, time


def version():
	with open("dbex/res/VERSION.txt") as file:
		return file.read()


__version__ = version()


class DBEXDecodeError(ValueError):
	# biraz çaldım gibi
	def __init__(self, msg, code, pos="Unknown"):

		code = (3 - len(str(code))) * '0' + str(code)
		errmsg = f"{msg} (Code: {code}): (char {pos})"
		ValueError.__init__(self, errmsg)

		self.code = code
		self.msg = msg
		self.pos = pos

	def __reduce__(self):
		return self.__class__, (self.msg, self.doc, self.pos)


class Decoder:
	default_tokenizers = "[{(\\,:\"')}]"
	header_shape = gvars.header_shape

	def __init__(self,
				 header=True,
				 default_path=None,
				 json_compability=1,
				 default_max_depth=0,
				 database_shape=None,
				 default_sort_keys=0,
				 encryption_pass=None,
				 changed_file_action=0,
				 default_decrypter=None,
				 default_header_path=None,
				 default_file_encoding="utf-8"):

		self.default_file_encoding = default_file_encoding
		self.changed_file_action = changed_file_action
		self.default_header_path = default_header_path
		self.default_decrypter = default_decrypter
		self.default_sort_keys = default_sort_keys
		self.default_max_depth = default_max_depth
		self.json_compability = json_compability
		self.encryption_pass = encryption_pass
		self.database_shape = database_shape
		self.default_path = default_path
		self.header = header

		self.default_gen_decrypter = None
		if self.default_decrypter is not None and self.default_decrypter.gen_support:
			self.default_gen_decrypter = self.default_decrypter

	def __tokenize(self, string, tokenizers=None):
		"""Verilen tokenizerları verilen string (ya da generator) 
		içinden alıp ayıklıyor (string değer kontrolü yok)

		Args:
			string (str): [string ya da stringi döndüren bir generator]
			tokenizers (str): tokenizerlar işte. Defaults to Decoder.default_tokenizers.

		Yields:
			str: her bir özel parça ve arasında kalanlar
		"""
		tokenizers = self.default_tokenizers if tokenizers is None else tokenizers
		# Son token indexi
		temp = ""
		last_token_index = 0
		ending_index = 0
		#   Ki bir daha token bulduğumzda eskisi
		# ile yeni bulunan arasını da yollayabilelim

		for index, char in enumerate(string):
			if char in tokenizers:
				# "" önlemek için
				if index > (last_token_index + 1):
					# son token ile şu anki token arasını yolla
					yield temp
				# tokenın kendinsini yolla
				yield char
				temp = ""
				# son token şimdiki token
				last_token_index = index

			else:
				temp += char
			ending_index = index
		if ending_index != last_token_index:
			yield temp

	def __tokenize_control(self, reader_gen, tokenizers=None):
		"""her ne kadar __tokenize fonksiyonunda tokenlara ayırmış olsak da 
		tırnak işaretlerinin lanetine yakalanmaktan kurtulmak için bu fonksiyonu kullanıyoruz

		Args:
			reader_gen (Decoder.read_gen(dosya_yolu)): parça parça okunan değerleri yollayan herhangi bir generator olabilir
			tokenizers (str): tokenizerlar işte. Defaults to Decoder.default_tokenizers.

		Raises:
			Exception: String dışında backslash kullanıldığında patlıyor

		Yields:
			str: her bir parça (ya token ya da element)
		"""
		errpos = 0
		tokenizers = self.default_tokenizers if tokenizers is None else tokenizers
		#   eğer tırnak işaret ile string değer
		# girilmeye başlanmışsa değerlerin kaydolacağı liste
		active_str = None
		# Hangi tırnak işaretiyle başladığımız
		is_string = False
		# Önceki elemanın \ olup olmadığı
		is_prv_bs = False

		for part in self.__tokenize(reader_gen, tokenizers):
			if part in ["'", '"', "\\"]:
				# Parça tırnak işaretiyse
				if part in ["'", '"']:
					# String içine zaten girdiysek
					if is_string:
						#       Eğer stringi açmak için kullanılan tırnak
						#   işaretiyle şu an gelen tırnak işareti
						# aynıysa string kapatılıyor (is_string False oluyor)
						is_string = False if is_string == part else is_string

						# Eğer string şimdi kapatıldıysa
						if not is_string:
							# Son parçayı aktif stringe ekle
							active_str.append(part)

							# Aktif stringi birleştirip yolla
							yield "".join(active_str)
							# Bu noktada neden aktif stringi listede topladığımı sorgulamaya başlıyorum

							# Sıfırla
							active_str = None
							is_string = False

						# Hala stringin içindeysek
						else:
							# Parçayı ekle
							active_str.append(part)
							# Diğer tırnak işareti olması ve \ için

					# String içine daha yeni giriyorsak
					else:
						# Hangi tırnakla girdiğimizi belirt
						is_string = part
						# Tırnağı aktif stringe ekle
						active_str = [part]

						#   aktif stringe tırnak ekleme sebebim ileride
						# string ve int değerlerin ayrımını kolaylaştırmak

						#   İlk başta .tags ve .data şeylerine sahip
						# olan bir class açmıştım ama şu an gereksiz görüyorum

						# Proje ne kadar uzadı be
						# Bu satıları kaç ay önce yazmıştım :-(

				elif part == "\\":
					# Lanet olası şey
					if is_string:

						# Önceki bu değilse anlam kazansın
						# Buysa anlamını yitirisin (\\ girip \ yazması için filan)
						if not is_prv_bs:
							active_str.append("\\")

						# Tersine çevir
						is_prv_bs = bool(1 - is_prv_bs)
						# lan ben bu değişkeni neden kullanmamışım
						# haydaaa neyse hallettim

					else:
						# String dışında kullanmak yasak
						raise DBEXDecodeError(
							"String dışında backslah kullanılamaz.",
							code=10,
							pos=errpos)
						# Karakter karakter okuduğum için satır sonlarında (\n) umarım sıkıntı çıkarmaz

			else:
				# Stringse ekle değilse yolla
				if is_string:
					active_str.append(part)

				# boşluklar eleniyor
				elif part.strip() != "":
					yield part

			errpos += len(part)

	def __convert(self,
				  generator_func,
				  index=0,
				  max_depth=None,
				  gen_lvl=0,
				  **kwargs):
		"""Verilen objenin nereye gideceğini yönlendiriyor ve generator

		Args:
			inputObj (function): generator döndüren fonksiyon
			index (int): generator functionun döndürdüğü generatora göre kaçıncı elementte olduğumuz gibi bir şey
			max_depth (int): Hangi derinliğe kadar generator olacağı. Defaults to class default.
			gen_lvl (elleme): kaçıncı derinlikte recursion yaptığımızı anlamak için
		
		Yields:
			objenin çevrilmiş hali
		"""

		# yapf: disable
		kwargs["max_depth"] = max_depth = self.default_max_depth if max_depth is None else max_depth
		kwargs["gen_lvl"] = gen_lvl + 1

		gen = generator_func()  # fonksiyondan bir tane generaotr koparıyoruz
		# element, index = next(gen), index+1 # sonraki elemana geçildi ve index de arttırıldı

		element, i = next(gen), 0  # 0. eleman çıkarıldı ve index değeri verildi
		while i < index:  # elemtimiz verilen indexteki element oluyor
			element, i = next(gen), i + 1

		if element in "[{(":
			# yapf: disable
			return self.__router(element, gen, generator_func, index=index, **kwargs)

		else:
			return self.__convert_obj(element)

		# try:
		# 	next(gen)
		# except StopIteration:
		# 	return rv
		# else:
		# 	raise DBEXDecodeError("Can convert up to 1 object only", 0)

	def __router(self,
		element,
		gen,
		generator_func,
		index=0,
		max_depth=None,
		gen_lvl=1,
		**kwargs):
		# yapf: disable
		kwargs["max_depth"] = max_depth = self.default_max_depth if max_depth is None else max_depth
		kwargs["gen_lvl"] = gen_lvl
		return_func = None

		if element == "[":
			next_closing = self.__find_next_closing(gen, type="[]")
			new_gen_func = lambda: (j for i, j in enumerate(generator_func())
				  if index < i <= next_closing)

			def list_gen():
				# convert_liste yeni generator_func verdiğimiz için index vermemiz gerekmiyor
				return (i for i in self.__convert_list(new_gen_func, **kwargs))

			return_func = list_gen

		elif element == "{":
			next_closing = self.__find_next_closing(gen, type="{}")
			new_gen_func = lambda: (j for i, j in enumerate(generator_func())
				  if index < i <= next_closing)

			def dict_gen():
				# yapf: disable
				return (i for i in self.__convert_dict(new_gen_func, **kwargs))

			return_func = dict_gen

		elif element == "(":
			next_closing = self.__find_next_closing(gen, type="()")
			new_gen_func = lambda: (j for i, j in enumerate(generator_func())
				  if index < i <= next_closing)

			def tuple_gen():
				# yapf: disable
				return (i for i in self.__convert_list(new_gen_func, tuple_mode=True, **kwargs))

			return_func = tuple_gen


		if ((max_depth == "all" or gen_lvl < max_depth)
		 and return_func.__name__ != "tuple_gen"):

			return return_func

		else:
			return self.gen_normalizer(return_func)

	def __convert_obj(self, element, json_compability=True):
		element = element.strip()

		if json_compability:
			if element == "null":
				return None
			elif element in ["true", "false"]:
				return True if element == "true" else False

		if element.isdigit():
			return int(element)

		elif element in ["None"]:
			return None

		# yapf: disable
		elif element.replace('.', '', 1).isdigit() or element in ["Infinity", "-Infinity", "NaN"]:
			return float(element)

		elif element in ["True", "False"]:
			return True if element == "True" else False

		else:
			raise DBEXDecodeError(
			 f"Undefined keyword : [{element}]", 0)

	def __convert_list(self, generator_func, tuple_mode=False, max_depth=None, **kwargs):
		max_depth = self.default_max_depth if max_depth is None else max_depth
		gen = generator_func()

		lui = -1
		ci = 0

		# Parantez kapatma değişkeni
		closing = ")" if tuple_mode else "]"
		# İstemediğimiz parantez kapatma şekilleri
		err_closing = "".join([i for i in "]})" if i != closing])

		index = 0
		for element in gen:
			if element == ",":
				ci += 1

			elif (ci - 1) == lui or element == closing:
				# '[NaN, true, [], []]'
				
				if element in "[{(":
					index
				
				yield self.__convert(generator_func, index=index, **kwargs)
    			lui+=1

			elif element in err_closing:
				raise DBEXDecodeError("Yanlis parantez kapatma: ['{element}']", code=0)

			else:
				# yapf: disable
    			raise DBEXDecodeError("Virgül koymadan yeni eleman eklenemez", code=20)
				# virgül koymadan yeni eleman eklenemiyor

			index += 1

	def __convert_dict(self, generator_func, max_depth=None, gen_lvl=None, **kwargs):
		pass

	def __find_next_closing(self, gen, index=0, type="[]"):
		"""sonraki parantez kapatma şeyini buluyor

		Args:
			gen (generator): Valla ne yaptığını hiç hatırlamıyorum
			index (int): kUSURA bakma
			type (str: "()", "[]", "{}"): [description]. Defaults to "[]".
			
		Returns:
			[type]: [description]
		"""
		cot = 1
		if len(type) != 2:
			raise Exception("Benim hatam...")

		for element in gen:
			# j, index = next(gen), index + 1
			index += 1
			if element == type[0]:
				cot += 1
			elif element == type[1]:
				cot -= 1

			if cot == 0:
				return index

		raise DBEXDecodeError

	def dump(self):
		pass

	def dumps(self):
		pass

	def dumper(self):
		pass

	def gen_normalizer(self, gen_func):
		"""__convert fonksiyonun generator fonksiyonunu objeye dönüştüren fonksiyon

		Args:
			gen_func (function): Generator döndüren fonksiyon alıyor (max_depth=0 __convert'ün çıktısı gibi)

		Returns:
			objenin gerçek formu 
		"""

		gen = gen_func()
		if gen_func.__name__ == "dict_gen":
			final = {}
			for key, value in gen:
				if callable(value):
					final[key] = self.gen_normalizer(value)
				else:
					final[key] = value

		elif gen_func.__name__ in ["list_gen", "tuple_gen"]:
			final = []
			for value in gen:
				if callable(value):
					final.append(self.gen_normalizer(value))
				else:
					final.append(value)

		return final

	def read(self,
	   path=None,
	   encoding=None,
	   decrypter=None,
	   sort_keys=None,
	   **kwargs):

		# sort keys olayına göz at
		encoding = self.default_file_encoding if encoding is None else encoding
		decrypter = self.default_decrypter if decrypter is None else decrypter
		path = self.default_path if path is None else path

		with open(path) as file:
			read = file.read()

		return decrypter(read, **kwargs) if decrypter is not None else read

	def read_gen(self,
		path=None,
		encoding=None,
		decrypter=None,
		max_depth=None,
		**kwargs):

		decrypter = self.default_gen_decrypter if decrypter is None else decrypter
		encoding = self.default_file_encoding if encoding is None else encoding
		path = self.default_path if path is None else path

		char = True
		with open(path) as file:
			while char:
				yield (char := file.read(1)) if decrypter is None else decrypter((char := file.read(1)))

	def read_gen_safe(self,
		  path=None,
		  encoding=None,
		  decrypter=None,
		  max_depth=None,
		  **kwargs):

		decrypter = self.default_gen_decrypter if decrypter is None else decrypter
		encoding = self.default_file_encoding if encoding is None else encoding
		path = self.default_path if path is None else path

		char = True
		index = -1
		while char:
			with open(path) as file:
				file.seek((index := index+1), 0)
				yield (char := file.read(1)) if decrypter is None else decrypter((char := file.read(1)))
