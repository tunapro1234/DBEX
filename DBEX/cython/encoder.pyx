# from dbex.lib.encryption import DBEXDefaultEncrypter as DefaultEncryptionClass
from dbex.sort_items import sorter as sorter_func
from dbex.encryption import DBEXMetaEncrypter
import dbex.globalv as gvars
# import types
# import time

__version__ = gvars.version()
"""
Eski encoder classı çok dağınıktı o yüzden yenisini yazıyorum ve burada biraz plan yapacağım
elimden geldiğince Decoder için uyumlu bir şema yazmaya çalışacağım onu da yenilemeyi düşünüyorum

bunda ana fonksiyon -> __convert olacak 

__convert bir generator olacağı için generator özelliğinin istenmediği 
durumlarda kapanma işlemi direkt olarak dump.. fonksiyonlarında yapılabilir

Sanırım bu yapıyı Decoder için de uygulayacağım
dumper ve loder uyumlu çalışabilmesi için __router gen_normalizer yapısında olacak

yani __router gen_func alacak ve list-dict ayrımı için gen_func.__name__e bakacak

peki __convert_list içinden __router çağırmak istersem ne olacak
eğer generator bize callable bir değer döndürürse bu değer __routera uçuyor ama eğer callacle bir değer göndermezse __converte
buraya kadar gayet iyi 
__convert bir generator olsa ve __routerı convert içine koysam

gelen değer gen_func, __convert() fonksiyonuna gönderiliyor. [gen_lvl = 0]
    convert içinde objenin dict veya list (ya da tuple) olup olmadığı kontrol ediliyor
    oradan __router(gen_lvl+1) iletiliyor veya direkt olarak değeri yieldlanıyor
        __router içinde dict ve list arasında seçim yapılıyor ve __init fonksiyonlarına gönderiliyorlar
            listenin ya da dictin her bir elemanı için __convert(gen_lvl) çağırılıyor

gelen değer obje, __convert() fonksiyonuna gönderiliyor. [gen_lvl = 0]
    convert içinde objenin dict veya list (ya da tuple) olup olmadığı kontrol ediliyor
    oradan __router(gen_lvl+1) iletiliyor veya direkt olarak değeri yieldlanıyor
    
    #   iletimde şöyle bir şey var, ben __router fonksiyonunu gen_normalizer şeklinde yazacağım o yüzden en başta normal obje verilirse,
    # gelen normal bir liste objesini __convertten __routera atarken ""def list_gen(): \n   return (i for i in list)"" içine almam gerekir
    
        __router içinde dict ve list arasında seçim yapılıyor ve __init fonksiyonlarına gönderiliyorlar
            listenin ya da dictin her bir elemanı için __convert(gen_lvl) çağırılıyor
    
""def list_gen(): \n   return (i for i in list)"" den başka ne olabilir
HMMmMMMMMmmmmmMMMMMMmmmMMmmmmMMMMMmMMmMmmMmmMMMM
__router içinde obje ya da generator olduğunu kontrol edebilirim yani eğer verilen gen_func objeyse farklı alır değilse farklı 
gayet kabul edilebilir duruyor
kesin bir bokluk çıkacak
ÇIKMADI AHAHHAHHAHAHH

"""

sort_keys_func = sorter_func


class Encoder:
    def __init__(self,
                 indent=0,
                 path=None,
                 sort_keys=0,
                 max_depth=0,
                 header=False,
                 allow_nan=True,
                 header_path=None,
                 json_compability=1,
                 database_shape=None,
                 encrypter_args=None,
                 encryption_obj=None,
                 changed_file_action=0,
                 file_encoding="utf-8",
                 seperators=(", ", ": "),
                 encrypter_kwargs=None):

        self.changed_file_action = changed_file_action
        self.json_compability = json_compability
        self.encrypter_kwargs = encrypter_kwargs
        self.encrypter_args = encrypter_args
        self.database_shape = database_shape
        self.file_encoding = file_encoding
        self.header_path = header_path
        self.seperators = seperators
        self.sort_keys = sort_keys
        self.max_depth = max_depth
        self.allow_nan = allow_nan
        self.indent = indent
        self.header = header
        self.path = path

        self.encryption_obj = encryption_obj

        self.encrypter = None
        self.encrypter_gen = None
        if encryption_obj is not None:
            if type(type(encryption_obj)) is DBEXMetaEncrypter:
                if encryption_obj.gen_encryption:
                    self.encrypter_gen = encryption_obj.gen_encrypter
                self.encrypter = encryption_obj.encrypter
            else:
                raise TypeError(
                    "Must use DBEXMetaEncrypter on Encryption class objects")

    def __convert(self,
                  inputObj,
                  max_depth=None,
                  gen_lvl=0,
                  allow_nan=None,
                  json_compability=None,
                  **kwargs):
        # indent
        # seperators

        # JSON COMPABILITY OLAYINA BAK

        json_compability = self.json_compability if json_compability is None else json_compability
        max_depth = self.max_depth if max_depth is None else max_depth
        allow_nan = self.allow_nan if allow_nan is None else allow_nan

        kwargs["json_compability"] = json_compability
        kwargs["max_depth"] = max_depth
        kwargs["alow_NaN"] = allow_nan
        kwargs["gen_lvl"] = gen_lvl + 1

        if callable(inputObj):
            for i in self.__router(inputObj, **kwargs):
                yield i

        else:
            if type(inputObj) in [list, dict, tuple]:
                for i in self.__router(inputObj, **kwargs):
                    yield i

            else:
                yield self.__convert_obj(inputObj, **kwargs)

    def __convert_obj(self,
                      inputObj,
                      json_compability=None,
                      allow_nan=None,
                      **kwargs):

        json_compability = self.json_compability if json_compability is None else json_compability
        allow_nan = self.allow_nan if allow_nan is None else allow_nan

        kwargs["json_compability"] = json_compability
        kwargs["allow_nan"] = allow_nan

        if inputObj is None:
            return "null" if json_compability else "None"

        elif type(inputObj) in [bool]:
            if json_compability:
                return "true" if inputObj else "false"

            else:
                return "True" if inputObj else "False"

        # yapf: disable
        elif inputObj in [float("Infinity"), float("-Infinity")] or inputObj != inputObj:

            if inputObj == float("Infinity"):
                return "Infinity"

            elif inputObj == float("-Infinity"):
                return "-Infinity"

            elif inputObj != inputObj:
                return "NaN"

        else:
            # yapf: disable
            return f'"{inputObj}"' if type(inputObj) == str else str(inputObj)

    def __router(self, inputObj, max_depth=None, gen_lvl=None, **kwargs):
        # gen level bu fonksiyonu çağıran __convert fonksiyonunda arttırılıyor
        max_depth = self.max_depth if max_depth is None else max_depth
        kwargs["max_depth"] = max_depth
        kwargs["gen_lvl"] = gen_lvl

        f_gen = None
        if callable(inputObj):
            gen = inputObj()
            if inputObj.__name__ == "dict_gen":
                f_gen = self.__convert_dict(gen, **kwargs)

            elif inputObj.__name__ == "list_gen":
                f_gen = self.__convert_list(gen, **kwargs)

            elif inputObj.__name__ == "tuple_gen":
                f_gen = self.__convert_list(gen, tuple_mode=True, **kwargs)

        else:
            if type(inputObj) == dict:
                f_gen = self.__convert_dict(inputObj.items(), **kwargs)

            elif type(inputObj) == list:
                f_gen = self.__convert_list(inputObj, **kwargs)

            elif type(inputObj) == tuple:
                f_gen = self.__convert_list(inputObj, tuple_mode=True, **kwargs)

        if max_depth == "all" or gen_lvl < max_depth:
            for i in f_gen:
                yield i
        else:
            yield "".join([i for i in f_gen])

    def __convert_list(self,
      iterable,
      tuple_mode=False,
      seperators=None,
      max_depth=None,
      indent=None,
      gen_lvl=1,
      **kwargs):

        seperators = self.seperators if type(seperators) != tuple else seperators
        max_depth = self.max_depth if max_depth is None else max_depth
        indent = self.indent if type(indent) != int else indent

        str_indent = " " * indent

        # yapf: disable
        comma = seperators[0].rstrip() if indent else seperators[0]

        kwargs["seperators"] = seperators
        kwargs["max_depth"] = max_depth
        kwargs["gen_lvl"] = gen_lvl
        kwargs["indent"] = indent

        # firstün olayı parantez açtıktan sonra virgül koymamasını sağlamak
        first = True
        # parantez açma
        yield "(" if tuple_mode else "["

        for element in iterable:
            if not first:
                # yapf: disable
                yield f"{comma}\n{str_indent * gen_lvl}" if indent else comma
                # parser ve indent yazdırma

            elif indent:
                # parantez açtıktan sonra indent yazdırma
                yield f"\n{str_indent * gen_lvl}"

            # Objemizi objenin ne olduğunun belirlendiği fonksiyona yolluyoruz
            # objemiz eğer list veya tuplesa bu fonksiyona recursion yapılıyor
            # eğer o tarz bir şey yoksa direkt olarak döndürülüyor

            # gen_lvl + 1 olarak veriyor, kontrol o fonksiyonda
            for i in self.__convert(element, **kwargs):
                #   eğer recursion yapıyorsak for döngüsünde kullandığım fonksiyon
                # kendi çağırdı bu fonksiyonun çıktılarını yield ile bize paslıyor
                # Biz de onu alıp daha yukarı paslıyoruz
                yield i

            # parantez açma şeyi sıfırlandı
            first = False

        if indent:
            yield f"\n{str_indent * (gen_lvl-1)}"
            # indent varsa parantez kapatmadan önce de boşluk bırak

        # parantez kapatma
        yield ")" if tuple_mode else "]"

    def __convert_dict(self,
      iterable,
      seperators=None,
      max_depth=None,
      indent=None,
      gen_lvl=1,
      **kwargs):

        seperators = self.seperators if type(seperators) != tuple else seperators
        max_depth = self.max_depth if max_depth is None else max_depth
        indent = self.indent if type(indent) != int else indent

        str_indent = " " * indent

        comma, colon = seperators[0].rstrip() if indent else seperators[0], seperators[1]

        kwargs["seperators"] = seperators
        kwargs["max_depth"] = max_depth
        kwargs["gen_lvl"] = gen_lvl
        # kwargs["indent"] = indent

        yield "{"
        first = True

        for key, value in iterable:
            if not first:
                # yapf: disable
                yield f"{comma}\n{str_indent * gen_lvl}" if indent else comma

            elif indent:
                yield f"\n{str_indent * gen_lvl}"

            # maalesef key değeri tuple olabiliyor ve bunun için recursion kullanıyoruz
            # eğer tuplesa recursion at değilse direkt olarak keyin değerini çevir
            # yapf: disable
            yield "".join([i for i in self.__convert(key, **kwargs, indent=0)])

            # : koydu
            yield colon

            # value döndürme
            # yukardakinin aynısı
            for i in self.__convert(value, **kwargs, indent=indent):
                yield i

            first = False

        # parantez kapatmadan önce indent
        if indent:
            yield f"\n{str_indent * (gen_lvl-1)}"
        # parantez kapatma
        yield "}"

    def dumps(self, inputObj, max_depth=None, sort_keys=None, **kwargs):
        """[summary]

        Args:
            inputObj (any): (generator döndüren fonksiyon da olabilir)
            max_depth (int):
            indent (int):
            sort_keys (bool):
            allow_nan (bool, optional):
            seperators ((str [virgül], str[iki nokta])):
        
        Returns:
            [type]: [description]
        """
        sort_keys = self.sort_keys if sort_keys is None else sort_keys
        max_depth = self.max_depth if max_depth is None else max_depth
        kwargs["max_depth"] = max_depth

        if sort_keys:
            max_depth = 0
            inputObj = sort_keys_func(inputObj)

        # yapf: disable
        if type(max_depth) is int and max_depth <= 0:
            return "".join([i for i in self.__convert(inputObj, **kwargs)])
        else:
            return self.__convert(inputObj, **kwargs)

    def dump(self,
             inputObj,
             file=None,
             encoding=None,
             max_depth=None,
             sort_keys=None,
             encryption_obj=None,
             encrypter_args=None,
             encrypter_kwargs=None,
             **kwargs):

        encrypter_kwargs = self.encrypter_kwargs if encrypter_kwargs is None else encrypter_kwargs
        encrypter_args = self.encrypter_args if encrypter_args is None else encrypter_args
        encrypter_kwargs = {} if encrypter_kwargs is None else encrypter_kwargs
        encrypter_args = [] if encrypter_args is None else encrypter_args

        encrypter_gen = encrypter = None
        if encryption_obj is not None:
            if type(type(encryption_obj)) is DBEXMetaEncrypter:
                if encryption_obj.gen_encryption:
                    encrypter_gen = encryption_obj.gen_encrypter
                encrypter = encryption_obj.encrypter

            else:
                raise TypeError("Must use DBEXMetaEncrypter on Encryption class objects")

        encrypter_gen = self.encrypter_gen if encrypter_gen is None else encrypter_gen
        encrypter = self.encrypter if encrypter is None else encrypter

        encoding = self.file_encoding if encoding is None else encoding
        sort_keys = self.sort_keys if sort_keys is None else sort_keys
        max_depth = self.max_depth if max_depth is None else max_depth
        file = self.path if file is None else file

        max_depth = self.max_depth if type(file) is not str else max_depth

        if sort_keys:
            inputObj = self.sort_keys_func(inputObj)


        # rv = "".join([i for i in self.__convert(inputObj, **kwargs)])
        if type(file) is not str or (
            type(max_depth) is int and max_depth <= 0):

            rv = "".join([i for i in self.__convert(inputObj, **kwargs)])

        else:
            rv = self.__convert(inputObj, **kwargs)
            encrypter = encrypter_gen if encrypter_gen is not None else encrypter


        if encrypter and encrypter == encrypter_gen and type(file) is str:
            return self.write_gen_safe(encrypter(rv, *encrypter_args, **encrypter_kwargs), path=file, encoding=encoding)

        elif encrypter:
            return self.write(encrypter(rv, *encrypter_args, **encrypter_kwargs), file=file, encoding=encoding)

        elif type(rv) is str: # file parametresi path değilse
            return self.write(rv, file=file, encoding=encoding)

        else:
            return self.write_gen_safe(rv, path=file, encoding=encoding)



    def write(self, string, file=None, encoding=None):
        """Verilen stringi verilen pathe yazdırır.

        Args:
            string ([type]): [description]
            path (str): Yazılacak dosyanın yolu. Defaults to class default.
            encoding (str, optional): file encoding methodu. Defaults to class default ("utf-8").
            mode (str): Dosyayı açma yöntemi, "w" ya da "w+". Defaults to "w+".
            encryption
        
        Returns:
            bool: İşlem başarılıysa True değilse False
        """

        encoding = self.file_encoding if encoding is None else encoding
        file = self.path if file is None else file

        try:
            if type(file) is str:
                with open(file, "w+", encoding=encoding) as f:
                    f.write(string)
            else:
                file.write(string)
        except:
            return False
        else:
            return True


    def write_gen(self, generator, path=None, encoding=None):
        """Generator objesinin döndürüğü stringleri verilen pathe yazdırır.

        Args:
            generator : str yieldlayan herhangi bir generator
            path (str): Yazılacak dosyanın yolu. Defaults to class default.
            encoding (str, optional): file encoding methodu. Defaults to class default ("utf-8").
        
        Returns:
            bool: İşlem başarılıysa True değilse False
        """
        encoding = self.file_encoding if encoding is None else encoding
        path = self.path if path is None else path

        try:
            with open(path, "w+", encoding=encoding) as file:
                file.write("")

            with open(path, "a", encoding=encoding) as file:
                for i in generator:
                    file.write(i)
        except:
            return False
        else:
            return True

    def write_gen_safe(self, generator, path=None, encoding=None):
        """Generator objesinin döndürüğü stringleri verilen pathe yazdırır (her seferinde açıp kapatarak).

        Args:
            generator : str yieldlayan herhangi bir generator
            path (str): Yazılacak dosyanın yolu. Defaults to class default.
            encoding (str, optional): file encoding methodu. Defaults to class default ("utf-8").
        
        Returns:
            bool: İşlem başarılıysa True değilse False
        """
        encoding = self.file_encoding if encoding is None else encoding
        path =  self.path if path is None else path

        try:
            with open(path, "w+", encoding=encoding) as file:
                file.write("")

            for i in generator:
                with open(path, "a", encoding=encoding) as file:
                    file.write(i)
        except:
            return False
        else:
            return True
