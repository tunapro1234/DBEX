from dbex.lib.encryption import encrypter as defaultEncrypter_func


def version():
    with open("dbex/res/VERSION.txt") as file:
        return file.read()


__version__ = version()


class Encoder:
    encrypter_func = defaultEncrypter_func

    header_shape = {
        "hash": [str],
        "version": [int],
        "database_shape": [list, dict],
        "header_hash": [str]
    }

    def __init__(self,
                 header=False,
                 encryption=None,
                 default_indent=0,
                 default_path=None,
                 default_max_depth=0,
                 database_shape=None,
                 default_sort_keys=0,
                 encryption_pass=None,
                 default_header_path=None,
                 changed_file_action=0,
                 default_seperators=(", ", ": "),
                 default_file_encoding="utf-8"):
        self.default_file_encoding = default_file_encoding
        self.default_header_path = default_header_path
        self.changed_file_action = changed_file_action
        self.default_seperators = default_seperators
        self.default_sort_keys = default_sort_keys
        self.default_max_depth = default_max_depth
        self.encryption_pass = encryption_pass
        self.default_indent = default_indent
        self.database_shape = database_shape
        self.default_path = default_path
        self.encryption = encryption
        self.header = header

    def __dump_gen_(self,
                    obj,
                    indent="",
                    max_depth=None,
                    seperators=None,
                    gen_lvl=1):

        # yukarda bunun kontrolünü yapmıştık
        if None in [max_depth, seperators, indent, gen_lvl]:
            raise Exception("Input cannot be None")

        if type(seperators) != tuple:  # or len(seperators) != 2
            raise Exception(f"Seperator error: {seperators}")

        # yapf: disable
        parser1, parser2 = seperators[0].rstrip() if indent else seperators[0], seperators[1]

        kwargs = {
            "element": None,
            "indent": indent,
            "max_depth": max_depth,
            "seperators": seperators,
            "gen_lvl": gen_lvl + 1
        }

        if type(obj) in [list, tuple]:
            # firstün olayı parantez açtıktan sonra virgül koymamasını sağlamak
            first = True
            # parantez açma
            yield "(" if type(obj) == tuple else "["

            for element in obj:
                if not first:
                    # parser ve indent yazdırma
                    # yapf: disable
                    yield parser1 + "\n" + indent * (gen_lvl + 1) if indent else parser1

                elif indent:
                    # parantez açtıktan sonra indent yazdırma
                    yield "\n" + indent * (gen_lvl + 1)

                # Objemizi objenin ne olduğunun belirlendiği fonksiyona yolluyoruz
                # objemiz eğer list dict veya tuplesa bu fonksiyona recursion yapılıyor
                # eğer o tarz bir şey yoksa direkt olarak döndürülüyor

                # gen_lvl + 1 olarak veriyor kontrol o fonksiyonda
                kwargs["element"] = element
                for i in self.__dump_gen(**kwargs):
                    #   eğer recursion yapıyorsak for döngüsünde kullandığım fonksiyon
                    # kendi çağırdı bu fonksiyonun çıktılarını yield ile bize paslıyor
                    # Biz de onu alıp daha yukarı paslıyoruz
                    yield i

                # parantez açma şeyi sıfırlandı
                first = False

            if indent:
                # indent varsa parantez kapatmadan önce de boşluk bırak
                yield "\n" + indent * gen_lvl

            # parantez kapatma
            yield ")" if type(obj) == tuple else "]"

        elif type(obj) == dict:
            yield "{"
            first = True

            for key, value in obj.items():
                if not first:
                    # yapf: disable
                    yield parser1 + "\n" + indent * (gen_lvl + 1) if indent else parser1

                elif indent:
                    yield "\n" + indent * (gen_lvl + 1)

                # maalesef key değeri tuple olabiliyor ve bunun için recursion kullanıyoruz
                # eğer tuplesa recursion at değilse direkt olarak keyin değerini çevir
                kwargs["element"] = key
                # yapf: disable
                yield "".join([i for i in self.__dump_gen_(**kwargs)]) if type(key) == tuple else self.__convert(key)

                # : koydu
                yield parser2

                # value döndürme
                # yukardakinin aynısı
                kwargs["element"] = value
                for i in self.__dump_gen(**kwargs):
                    yield i

                first = False

            # parantez kapatmadan önce indent
            if indent:
                yield "\n" + indent * gen_lvl
            # parantez kapatma
            yield "}"

        else:
            yield obj
            # tunapro1234 10.23 - 14/09/20

    def __dump_gen(self,
                   element,
                   indent=None,
                   max_depth=None,
                   seperators=None,
                   gen_lvl=0):
        # default şeylerin ayarlanması
        indent = self.default_indent if indent is None else indent
        max_depth = self.default_max_depth if max_depth is None else max_depth
        seperators = self.default_seperators if seperators is None else seperators
        ###

        indent = " " * indent if type(indent) == int else indent

        kwargs = {
            "obj":element,
            "indent":indent,
            "max_depth":max_depth,
            "seperators":seperators,
            "gen_lvl":gen_lvl
        }

        if type(element) in [tuple, list, dict]:
            if gen_lvl < max_depth or max_depth == "all":
                # maximum generator derinliği aşılmadıysa yield
                for i in self.__dump_gen_(**kwargs):
                    yield i
            else:
                # maximum generator derinliği aşıldığında direkt olarak dönndürüyor
                yield "".join([
                    i for i in self.__dump_gen_(**kwargs)
                ])
        else:
            yield self.__convert(element)

    def __convert(self, element):
        json = True
        if element in [float("Infinity"),
                       float("-Infinity")] or element != element:
            if element == float("Infinity"):
                return "Infinity"
            elif element == float("-Infinity"):
                return "-Infinity"
            elif element != element:
                return "NaN"

        elif json and element is None or type(element) == bool:
            if element is None:
                return "null"
            elif element == True:
                return "true"
            elif element == False:
                return "false"

        else:
            return f'"{element}"' if type(element) == str else str(element)

    def sort_keys(self, rv, *args, **kwargs):
        return rv

    def dumps(self, obj, sort_keys=None, max_depth=None, **kwargs):
        """ json.dumpsın çakması + generator özelliği
        Eğer (obje dışında) herhangi bir değere None verilirse Encoder objesinde verilen default değerini alır.

        Args:
            obj (any): Encode edilecek obje
            indent (int, optional): Düzen için filan kaç boşluk bırakılcak gibi bir şey 4 yap baya güzel oluyor. Defaults to 0.
            max_depth (int, str, optional): Generatorların ne kadar derine ineceği. Defaults to 0.
            seperators ((str [virgül], str [iki nokta]), optional): [description]. Defaults to (", ", ": ").
            sort_keys (int, optional): objenin içindeki dictlerin keylere göre sıralanıp sıralanmayacağı (Aktif edilirse generator özelliği kalkıyor). Defaults to 0.

        Returns:
            Encoded object or a function that returns a generator which yields encoded object
            kayraaaaaaa
        """

        kwargs["element"] = obj
        kwargs["max_depth"] = self.default_max_depth if max_depth is None else max_depth
        sort_keys = self.default_sort_keys if sort_keys is None else sort_keys

        if sort_keys:
            return self.sort_keys("".join(
                                            [i for i in self.__dump_gen(**kwargs)]
                                         ))
        else:
            if kwargs["max_depth"] > 0:
                return lambda: self.__dump_gen(**kwargs)
            else:
                return "".join([i for i in self.__dump_gen(**kwargs)])


    def dump(self, obj, file_path, **kwargs):
        self.write(file_path, self.encrypter_func(dumps(obj, **kwargs)))

    def write(self, string, path=None, encoding=None):
        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        with open(path, "w+") as file:
            file.write(string)

    def write_gen(self, generator, path=None, encoding=None):
        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        with open(path, "w+") as file:
            file.write("")

        with open(path, "a") as file:
            for i in generator:
                file.write(i)

    def write_gen_safe(self, generator, path=None, encoding=None):
        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        with open(path, "w+") as file:
            file.write("")

        for i in generator:
            with open(path, "a") as file:
                file.write(i)


def test():
    return


if __name__ == "__main__":
    test()