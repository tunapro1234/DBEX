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
                 default_path=None,
                 default_file_encoding=None,
                 encryption=None,
                 encryption_pass=None,
                 header=None,
                 default_mex_gen_lvl=None,
                 default_header_path=None,
                 changed_file_action=None,
                 database_shape=None,
                 database_form_gen_lvl=None):
        self.default_header_path = default_header_path
        self.changed_file_action = changed_file_action
        self.default_max_gen_lvl = default_mex_gen_lvl
        self.default_encoding = default_file_encoding
        self.encryption_pass = encryption_pass
        self.database_form = database_shape
        self.default_path = default_path
        self.encryption = encryption
        self.header = header

    def __dump_gen_(self,
                    obj,
                    max_gen_lvl=1,
                    gen_lvl=1,
                    indent="",
                    seperators=(", ", ": ")):
        if type(seperators) != tuple or len(seperators) != 2:
            raise Exception("Seperator error")

        parser1, parser2 = seperators[0].rstrip(
        ) if indent else seperators[0], seperators[1]

        if type(obj) in [list, tuple]:
            # firstün olayı parantez açtıktan sonra virgül koymamasını sağlamak
            first = True
            # parantez açma
            yield "(" if type(obj) == tuple else "["

            for element in obj:
                if not first:
                    # parser ve indent yazdırma
                    yield parser1 + "\n" + indent * (gen_lvl +
                                                     1) if indent else parser1

                elif indent:
                    # parantez açtıktan sonra indent yazdırma
                    yield "\n" + indent * (gen_lvl + 1)

                # Objemizi objenin ne olduğunun belirlendiği fonksiyona yolluyoruz
                # objemiz eğer list dict veya tuplesa bu fonksiyona recursion yapılıyor
                # eğer o tarz bir şey yoksa direkt olarak döndürülüyor

                # gen_lvl + 1 olarak veriyor kontrol o fonksiyonda
                for i in Encoder.__dump_gen(element, max_gen_lvl, gen_lvl + 1,
                                            indent):
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
                    yield parser1 + "\n" + indent * (gen_lvl +
                                                     1) if indent else parser1

                elif indent:
                    yield "\n" + indent * (gen_lvl + 1)

                # maalesef key değeri tuple olabiliyor ve bunun için recursion kullanıyoruz
                # eğer tuplesa recursion at değilse direkt olarak keyin değerini çevir
                yield "".join([
                    i
                    for i in Encoder.__dump_gen_(key, max_gen_lvl, gen_lvl, "")
                ]) if type(key) == tuple else Encoder.__convert(key)
                # : koydu
                yield parser2

                # value döndürme
                # yukardakinin aynısı
                for i in Encoder.__dump_gen(value, max_gen_lvl, gen_lvl + 1,
                                            indent):
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
                   max_gen_lvl=0,
                   gen_lvl=0,
                   indent=0,
                   seperators=(", ", ": ")):
        indent = " " * indent if type(indent) == int else indent

        if type(element) in [tuple, list, dict]:
            if gen_lvl < max_gen_lvl:
                for i in Encoder.__dump_gen_(element, max_gen_lvl, gen_lvl,
                                             indent, seperators):
                    yield i
            else:
                yield "".join([
                    i for i in Encoder.__dump_gen_(element, max_gen_lvl,
                                                   gen_lvl, indent, seperators)
                ])
        else:
            yield Encoder.__convert(element)

    def __convert(self, element):
        if element in [float("Infinity"),
                       float("-Infinity")] or element != element:
            if element == float("Infinity"):
                return "Infinity"
            elif element == float("-Infinity"):
                return "-Infinity"
            elif element != element:
                return "NaN"
        else:
            return f'"{element}"' if type(element) == str else str(element)

    def sort_keys(self, rv, *args, **kwargs):
        return rv

    def dumps(self, obj, sort_keys=0, **kwargs):
        if sort_keys:
            return Encoder.sort_keys("".join(
                [i for i in Encoder.__dump_gen(obj, **kwargs)]))
        else:
            return "".join([i for i in Encoder.__dump_gen(obj, **kwargs)])

    def dumps(self,
              obj,
              max_gen_lvl=0,
              indent=0,
              seperators=(", ", ": "),
              sort_keys=0):
        if sort_keys:
            return Encoder.sort_keys("".join([
                i for i in Encoder.__dump_gen(
                    obj, max_gen_lvl=0, indent=0, seperators=(", ", ": "))
            ]))
        else:
            return "".join([
                i for i in Encoder.__dump_gen(
                    obj, max_gen_lvl=0, indent=0, seperators=(", ", ": "))
            ])

    def dump(self, obj, file_path, **kwargs):
        Encoder.write(file_path, Encoder.encrypter_func(dumps(obj, **kwargs)))

    def write(self, rv, *args, **kwargs):
        return rv


def test():
    return


if __name__ == "__main__":
    test()