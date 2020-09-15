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

gen_normalizer ile çevirme load... fonksiyonlarında yapılacak

    convert generator döndüren fonksiyon alıyor onu routera atıyor router 
içinde generator kısıtlanıp fonksiyonla wrapplanip convert_listlere filan gönderiliyor

ama convert objeleri nasıl dönecek
__convert(lambda: (__tokenize_gen(__tokenize(string or generator))))
normalde __load ilk elemana bakıp yolluyordu biz de o tarz bir şey yapabilirz
__convert yerine __main yapsam main içinden __converte atsa daha hoş olur

__convert_obj yaptım
hadi başlayalım
"""

from dbex.lib.encryption import decrypter
import dbex.res.globalv as gvars
import types, time


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
                 encryption=None,
                 default_path=None,
                 default_max_depth=0,
                 database_shape=None,
                 default_sort_keys=0,
                 encryption_pass=None,
                 default_header_path=None,
                 changed_file_action=0,
                 default_file_encoding="utf-8"):
        self.default_file_encoding = default_file_encoding
        self.changed_file_action = changed_file_action
        self.default_header_path = default_header_path
        self.default_sort_keys = default_sort_keys
        self.encryption_pass = encryption_pass
        self.default_max_depth = default_max_depth
        self.database_shape = database_shape
        self.default_path = default_path
        self.encryption = encryption
        self.header = header

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

    def __tokenize_check(self, reader_gen, tokenizers=None):
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

                elif part == "\\":
                    # Lanet olası şey
                    if is_string:
                        # Önceki bu değilse anlam kazansın
                        # Buysa anlamını yitirisin (\\ girip \ yazması için filan)
                        is_prv_bs = bool(1 - is_prv_bs)
                        active_str.append("\\")

                        # oysa ki seni kullanmayı çok isterdim
                        # if (is_prv_bs := bool(1 - is_prv_bs)):
                        #     active_str.append("\\")
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

                elif part.strip() != "":
                    yield part

            errpos += len(part)

    def __convert(self):
        pass

    def __convert_obj(self):
        pass

    def __convert_list(self):
        pass

    def __convert_dict(self):
        pass

    def __find_next_closing(self):
        pass

    def gen_normalizer(self):
        pass

    def dump(self):
        pass

    def dumps(self):
        pass

    def dumper(self):
        pass

    # path=None, encoding=None, encryptor=None, max_depth=None, sort_keys=None, **kwargs

    def read(self):
        pass

    def read_gen(self):
        pass

    def read_gen_safe(self):
        pass
