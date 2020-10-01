# from dbex.lib.encryption import DBEXDefaultEncrypter as DefaultEncryptionClass
from dbex.lib.sort_items import sorter as sorter_func
from dbex.lib.encryption import DBEXMetaEncrypter
import dbex.res.globalv as gvars
# import types
# import time

__version__ = gvars.version()
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


sort_keys_func = sorter_func


class Decoder:
    default_tokenizers = "[{(\\,:\"')}]"
    header_shape = gvars.header_shape

    def __init__(self,
                 path=None,
                 sort_keys=0,
                 header=False,
                 max_depth="all",
                 header_path=None,
                 json_compability=1,
                 database_shape=None,
                 decrypter_args=None,
                 encryption_obj=None,
                 decrypter_kwargs=None,
                 file_encoding="utf-8",
                 changed_file_action=0):

        self.changed_file_action = changed_file_action
        self.json_compability = json_compability
        self.decrypter_kwargs = decrypter_kwargs
        self.encryption_obj = encryption_obj
        self.decrypter_args = decrypter_args
        self.database_shape = database_shape
        self.file_encoding = file_encoding
        self.header_path = header_path
        self.sort_keys = sort_keys
        self.max_depth = max_depth
        self.header = header
        self.path = path

        self.decrypter = None
        self.decrypter_gen = None
        if encryption_obj is not None:
            if type(type(encryption_obj)) is DBEXMetaEncrypter:
                if encryption_obj.gen_encryption:
                    self.decrypter_gen = encryption_obj.gen_decrypter
                self.decrypter = encryption_obj.decrypter
            else:
                raise TypeError(
                    "Must use DBEXMetaEncrypter on Encryption class objects")

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

        # gen_func verilirse uyum sağlamak için
        # while not isinstance(string, Iterable):
        string = string() if callable(string) else string

        for index, char in enumerate(string):
            # 	eğer string yerine generator verilirse ve bu
            # generator ", " şeklinde döndürürse sıkıntı olmasın diye strip
            if char.strip() != "" and char.strip() in tokenizers:
                # "" önlemek için
                if index > (last_token_index + 1):
                    # son token ile şu anki token arasını yolla
                    yield temp
                # tokenın kendinsini yolla
                yield char.strip()
                temp = ""
                # son token şimdiki token
                last_token_index = index

            else:
                temp += char
            ending_index = index
        if ending_index != last_token_index:
            yield temp

    def __tokenize_control(self, reader_gen, tokenizers=None):
        """Her ne kadar __tokenize fonksiyonunda tokenlara ayırmış olsak da 
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
        """Verilen objenin nereye gideceğini yönlendiriyor ve generator DEĞİL

		Args:
			generator_func (function): generator döndüren fonksiyon
			max_depth (int): Hangi derinliğe kadar generator olacağı. Defaults to class default.
			index (int, elleme): generator functionun döndürdüğü generatora göre kaçıncı elementte olduğumuz gibi bir şey
			gen_lvl (int, elleme): kaçıncı derinlikte recursion yaptığımızı anlamak için
		
		Returns:
			objenin çevrilmiş hali
		"""

        # yapf: disable
        kwargs["max_depth"] = max_depth = self.max_depth if max_depth is None else max_depth
        # max_depth default ayarlaması
        kwargs["gen_lvl"] = gen_lvl + 1
        # gen_lvl sadece burada arttırılıyor

        if (gen := generator_func()) is None:  # fonksiyondan bir tane generaotr koparıyoruz
            raise DBEXDecodeError("Okuma hatasi", code=0)

        # 	Şimdi bize bir index veriliyor ve bu index, dönüştürülmesi istenen objenin
        # generator_functionın döndürdüğü generatorın kaçıncı elemanı olduğunun sayacı
        # Biz de bu objeye gidebilmek için aşağıdaki while döngüsünü kullanıyoruz
        element, i = next(gen), 0  # 0. eleman çıkarıldı ve index değeri verildi
        while i < index:  # elemtimiz verilen indexteki element oluyor
            element, i = next(gen), i + 1

        # 	Eğer eleman recursion gerektiren
        # bir parça olduğuna işaret ediyorsa
        if element in "[{(":
            # yapf: disable
            return self.__router(element, gen, generator_func, index=index, **kwargs)
            # yardımcı fonksiyona

        else:
            # Normal parçayı çevirmesi için diğer yardımcı fonksiyon
            return self.__convert_obj(element)

        # ne demem gerektiğini bilmiyorum
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
        """__convert için yardımcı fonksiyon, __convert_list ya da __convert_gen'e gideceğini belirliyor

		Args:
			element (any): Generatordan son çıkarılan eleman
			gen (generator): Kullanılmış (ya da kullanılmamış) obje'nin generatoru
			generator_func (function): gen'i döndürebilecek fonksiyon 
			max_depth (int): Hangi derinliğe kadar generator olacağı. Defaults to class default.
			index (int, elleme): generator functionun döndürdüğü generatora göre kaçıncı elementte olduğumuz gibi bir şey
			gen_lvl (int, elleme): kaçıncı derinlikte recursion yaptığımızı anlamak için

		Returns:
			dict, list ya da generator_function 
		"""

        # yapf: disable
        kwargs["max_depth"] = max_depth = self.max_depth if max_depth is None else max_depth
        # default ayarlama şeyleri
        kwargs["gen_lvl"] = gen_lvl
        return_func = None

        # 							Şimdi hızlıca özet geçeceğim. biz ilgili __convert_.. fonksiyonuna generator_function'ı
        # 						iletirken bu generator_function'ı boyutunu sadece dönüştürmek istediğimiz objenin boyuna
        # 					azaltarak iletiyoruz. Temelde bunu yapma sebebimizden emin değilim direkt olarak index de
        # 				verebilrmişim aslında (ben malım). Neyse çevirmeye zamanım olduğunu düşünmüyorum ayrıca şu anda
        # 			aklıma gelmeyen bir sebebi de olabilir. Eski taslakları incelemek lazım, neyse. Küçültmek için öneclikle
        # 		aktif parantezin kapanışının indexi bulunuyor sonra şu anki indexle (yani parantezin açılşı) kapanış arasına
        # 	ksııtlanıyor. Sonra gen_normalizer tarafında anlaşılabilecek bir fonksiyon yaratıyorum ve bu fonksiyon bir generator
        # döndürüyor. Bu generator da kendi aldığı gen_normalizer'ı anlamlandırıyor

        # Ayrıca gen_lvl ve max_depth kontrolü de burada yapılıyor, aşılmışsa gen_normalizer'a yollanıyor

        if element == "[":
            next_closing = self.__find_next_closing(gen, index=index, b_type="[]")
            new_gen_func = lambda: (j for i, j in enumerate(generator_func()) if index < i <= next_closing)

            def list_gen():
                # convert_liste yeni generator_func verdiğimiz için index vermemiz gerekmiyor
                return (i for i in self.__convert_list(new_gen_func, **kwargs))

            return_func = list_gen

        elif element == "{":
            next_closing = self.__find_next_closing(gen, index=index, b_type="{}")
            new_gen_func = lambda: (j for i, j in enumerate(generator_func())
               if index < i <= next_closing)

            def dict_gen():
                # yapf: disable
                return (i for i in self.__convert_dict(new_gen_func, **kwargs))

            return_func = dict_gen

        elif element == "(":
            next_closing = self.__find_next_closing(gen, index=index, b_type="()")
            new_gen_func = lambda: (j for i, j in enumerate(generator_func())
               if index < i <= next_closing)

            def tuple_gen():
                # yapf: disable
                return (i for i in self.__convert_list(new_gen_func, tuple_mode=True, **kwargs))

            return self.gen_normalizer(tuple_gen)
            # return_func = tuple_gen


        if type(max_depth) == int and gen_lvl <= max_depth:
            return self.gen_normalizer(return_func, recursion=False)

        elif type(max_depth) == str and max_depth == "all":
            return self.gen_normalizer(return_func)

        else:
            return return_func

    def __convert_obj(self, element, json_compability=True):
        """Verilen str objeyi anlamlandırıyor

		Args:
			element (str): obje
			json_compability (bool, optional): json uyumluluğu. Defaults to True.

		Raises:
			DBEXDecodeError: Tanımlanmamış obje

		Returns:
			Objenin gerçek formu
		"""
        element = element.strip()

        if json_compability:
            if element == "null":
                return None
            elif element in ["true", "false"]:
                return True if element == "true" else False

        if element.isdigit():
            return int(element)

        elif element[0] in "\"'" and element[-1] in "\"'" and element[0] == element[-1]:
            return element[1:-1]

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

    def __convert_list(self, generator_func, tuple_mode=False, **kwargs):
        gen = generator_func()

        # last used index
        lui = -1
        # current index
        ci = 0

        # Parantez kapatma değişkeni
        closing = ")" if tuple_mode else "]"
        # İstemediğimiz parantez kapatma şekilleri
        err_closing = "".join([i for i in "]})" if i != closing])
        # virgül kontroolü için


        index = 0
        for element in gen:
            if element.strip() == ",":
                # kullanılabilecek index arttırıldı
                ci += 1

            elif element.strip() == closing:
                # Buraya hiç girilmiyor (çünkü __router parantez kapatmayı generator_function içine dahil etmiyor)
                # yine de yazmakta fayda var
                #	- yoo giriyor (gelecekteki ve kendinin mal olduğunun farkında olan tuna)
                break

            elif element.strip() in err_closing:
                raise DBEXDecodeError("Yanlis parantez kapatma: ['{element}']", code=0)

            # eğer kullanıma açık yer varsa
            elif (ci - 1) == lui:
                # objeyi dönüştür
                yield self.__convert(generator_func, index=index, **kwargs)

                # index arttırma
                if element in "[{(":
                    b_type=None
                    # 	bu tarz şeylerde
                    # kısaltma olmamsı beni üzüyor
                    if element == "(":
                        b_type = "()"
                    elif element == "[":
                        b_type = "[]"
                    elif element == "{":
                        b_type = "{}"
                    # index ve gen başlangıcı verilen objenin sonuna götürülüyor
                    index = self.__find_next_closing(gen, index=index, b_type=b_type)

                # kullanılan index arttırıldı
                lui+=1

            else:
                # yapf: disable
                raise DBEXDecodeError("Virgül koymadan yeni eleman eklenemez", code=20)
                # virgül koymadan yeni eleman eklenemiyor

            # index arttırıldı
            index += 1

    def __convert_dict(self, generator_func, **kwargs):
        gen = generator_func()
        index = 0

        # aktif olarak döndürülecek hangi değere yazığımız, key ya da valueya yazdığımızı gösteriyor
        # eğer keye yazmaya çalışıyorsak 0, valueya yazmaya çalışıyorsak 1
        cursor = 0
        cur_value = []
        err_closing = ")]"
        for element in gen:
            if element.strip() == "}":
                if len(cur_value) == 2:
                    yield tuple(cur_value)
                if len(cur_value) not in [0, 2]:
                    raise DBEXDecodeError("Not Implemented", 0)
                break

            elif element in err_closing:
                raise DBEXDecodeError("Not Implemented", 0)

            elif element.strip() == ":":
                if len(cur_value) == 1:
                    cursor = 1
                else:
                    raise DBEXDecodeError("Not Implemented", 0)

            elif element.strip() == ",":
                if len(cur_value) != 2:
                    raise DBEXDecodeError("Not Implemented", 0)

                yield tuple(cur_value)
                cur_value, cursor = [], 0

            else:
                converted_element = self.__convert(generator_func, index=index, **kwargs)

                # index atlama
                if element in "[{(":
                    b_type=None
                    if element == "(":
                        b_type = "()"
                    elif element == "[":
                        b_type = "[]"
                    elif element == "{":
                        b_type = "{}"

                    index = self.__find_next_closing(gen, index=index, b_type=b_type)


                # eğer key yazıyorsak ve gelen eleman dict ya da list ise hata verdir
                if (cursor == 0 and len(cur_value) == 0) and (
                 type(converted_element) in [list, dict] or (callable(converted_element) and converted_element.__name__ in ["list_gen", "dict_gen"])):
                    raise DBEXDecodeError("Not Implemented", 0)

                cur_value.append(converted_element)
                # if len(cur_value) == 2:
                # 	yield tuple(cur_value)


            index = index + 1

    def __find_next_closing(self, gen, index=0, b_type="[]"):
        """sonraki parantez kapatma şeyini buluyor

		Args:
			gen (generator): Valla ne yaptığını hiç hatırlamıyorum
			index (int): kUSURA bakma
			b_type (str: "()", "[]", "{}"): [description]. Defaults to "[]".
			
		Returns:
			[b_type]: [description]
		"""
        cot = 1
        if len(b_type) != 2:
            raise Exception("Benim hatam...")

        for element in gen:
            # j, index = next(gen), index + 1
            index += 1
            if element == b_type[0]:
                cot += 1
            elif element == b_type[1]:
                cot -= 1

            if cot == 0:
                return index

        raise DBEXDecodeError("parantezin kapanisi bulanamadi", 0)

    def loads(self, inputObj, max_depth=None, sort_keys=None, **kwargs):
        sort_keys = self.sort_keys if sort_keys is None else sort_keys
        max_depth = self.max_depth if max_depth is None else max_depth
        kwargs["max_depth"] = "all" if sort_keys else max_depth

        final = self.__convert(lambda: self.__tokenize_control(inputObj), **kwargs)
        return sort_keys_func(final) if sort_keys else final

    def load(self,
             file=None,
             max_depth=None,
             sort_keys=None,
             encoding=None,
             encryption_obj=None,
             decrypter_args=None,
             decrypter_kwargs=None,
             **kwargs):

        # max_depth = None # vazgeçtim
        decrypter_kwargs = self.decrypter_kwargs if decrypter_kwargs is None else decrypter_kwargs
        decrypter_args = self.decrypter_args if decrypter_args is None else decrypter_args
        decrypter_kwargs = {} if decrypter_kwargs is None else decrypter_kwargs
        decrypter_args = [] if decrypter_args is None else decrypter_args

        decrypter_gen = decrypter = None
        if encryption_obj is not None:
            if type(type(encryption_obj)) is DBEXMetaEncrypter:
                if encryption_obj.gen_encryption:
                    decrypter_gen = encryption_obj.gen_decrypter
                decrypter = encryption_obj.decrypter

            else:
                raise TypeError("Must use DBEXMetaEncrypter on Encryption class objects")

        decrypter_gen = self.decrypter_gen if decrypter_gen is None else decrypter_gen
        decrypter = self.decrypter if decrypter is None else decrypter


        max_depth = self.max_depth if max_depth is None else max_depth # load ve dumpta max_depth iptal -yoo (gelecekteki tuna)
        sort_keys = self.sort_keys if sort_keys is None else sort_keys
        kwargs["max_depth"] = "all" if sort_keys else max_depth

        encoding = self.file_encoding if encoding is None else encoding
        file = self.path if file is None else file

        if decrypter_gen:
            generator_func = lambda: self.__tokenize_control(
                decrypter(self.read_gen(file=file, encoding=encoding),
                        *decrypter_args, **decrypter_kwargs))
        elif decrypter:
            generator_func = lambda: self.__tokenize_control(
                decrypter(self.read(file=file, encoding=encoding),
                        *decrypter_args, **decrypter_kwargs))

        else:
            generator_func = lambda: self.__tokenize_control(
                self.read(file=file, encoding=encoding))


        final = self.__convert(generator_func, **kwargs)
        return sort_keys_func(final) if sort_keys else final
        # return self.__convert(generator_func, **kwargs)

    def gen_normalizer(self, gen_func, recursion=True):
        """__convert fonksiyonun generator fonksiyonunu objeye dönüştüren fonksiyon

		Args:
			gen_func (function): Generator döndüren fonksiyon alıyor (max_depth=0 __convert'ün çıktısı gibi)

		Returns:
			objenin gerçek formu 
		"""
        # pylint hata önlemek için
        final = None
        gen = gen_func()
        if gen_func.__name__ in ["list_gen", "tuple_gen"]:
            final = []
            for value in gen:
                if callable(value) and recursion:
                    final.append(self.gen_normalizer(value))
                else:
                    final.append(value)

        elif gen_func.__name__ == "dict_gen":
            final = {}
            for key, value in gen:
                if callable(value) and recursion:
                    final[key] = self.gen_normalizer(value)
                else:
                    final[key] = value

        return tuple(final) if gen_func.__name__ == "tuple_gen" else final

    def read(self, file=None, encoding=None):
        # sort keys olayına göz at
        # decrypter = self.default_decrypter if decrypter is None else decrypter
        encoding = self.file_encoding if encoding is None else encoding
        file = self.path if file is None else file

        # file = open(file) if type(file) is str else file
        # read = file.read()
        # file = file.close() if type(file) is str else file

        if type(file) is str:
            with open(file, encoding=encoding) as file:
                return file.read()
        else:
            return file.read()

    def read_gen(self, file=None, encoding=None):
        encoding = self.file_encoding if encoding is None else encoding
        file = self.path if file is None else file

        # char = True
        # file = open(file) if type(file) is str else file
        # while char:
        #     yield (char := file.read(1))
        # file = file.close() if type(file) is str else file

        char = True
        if type(file) is str:
            with open(file, encoding=encoding) as file:
                while char:
                    yield (char := file.read(1))
        else:
            while char:
                yield (char := file.read(1))


    def read_gen_safe(self, path=None, encoding=None):
        encoding = self.file_encoding if encoding is None else encoding
        path = self.path if path is None else path

        char = True
        index = -1
        while char:
            with open(path) as file:
                file.seek((index := index+1), 0)
                yield (char := file.read(1))

    def sort_keys(self, rv, *args, **kwargs):
        return rv
