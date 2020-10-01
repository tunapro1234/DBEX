import dbex.res.globalv as gvars

__version__ = gvars.version()

"""

Hızlıca bir iki plan yapayım

Şimdi Encoder ve Decodera metaclassı BaseEncrypter olan bir classın objesi verilecek

eğer encryption generator olarak yapılmıyorsa cls.gen_encryption False oluyor
gen_encrypter ve gen_decrypter kullanılmayacaksa başta None yapılır, encrypter ve decryptera pointer 
olarak kullanılacaksa __init__de verilebilir


"""


class DBEXMetaEncrypter(type):
    def __new__(cls, name, bases, body):
        # print(cls, name, bases, body, sep="\n")
        attributes = [
            "encrypter", "decrypter", "gen_encrypter", "gen_decrypter",
            "gen_encryption"
        ]

        for attr in attributes:
            if attr not in body:
                raise TypeError(f"Required attribute not found: {attr}")

        return super().__new__(cls, name, bases, body)


class ExampleEncrypter1(metaclass=DBEXMetaEncrypter):
    gen_encryption = True

    def __init__(self, password=2909, sep="."):
        self.password = int(password)
        self.sep = sep

    def __encrypt(self, chr_):
        return ord(chr_)

    def __decrypt(self, ord_):
        return chr(ord_)

    def gen_encrypter(self, generator, *a, **kw):
        for i in generator:
            for char in i:
                yield self.__encrypt(char)
                yield self.sep

    def gen_decrypter(self, generator, *a, **kw):
        temp = ""
        for i in generator:
            for char in i:
                if char == self.sep:
                    yield self.__decrypt(temp)
                    temp = ""
                else:
                    temp += char

    def encrypter(self, string, *a, **kw):
        return "".join([i for i in self.gen_encrypter(string)])

    def decrypter(self, string, *a, **kw):
        return "".join([i for i in self.gen_decrypter(string)])


class ExampleEncrypter2(metaclass=DBEXMetaEncrypter):
    gen_encryption = None
    gen_encrypter = None
    gen_decrypter = None

    # key = Fernet.generate_key()

    def __init__(self, key, sep):
        try:
            from cryptography.fernet import Fernet
        except:
            print("Try: pip3 install cryptography")

        self.fernet_obj = Fernet(key)
        self.sep = sep

    def encrypter(self, string, *a, **kw):
        return self.fernet_obj.encrypt(string.encode())

    def decrypter(self, string, *a, **kw):
        return self.fernet_obj.decrypt(string.encode())


class ExapmleEncrypter3(metaclass=DBEXMetaEncrypter):
    gen_encryption = True
    gen_encrypter = None
    gen_decrypter = None

    def __init__(self, num=2):
        self.gen_encrypter = self.encrypter
        self.gen_decrypter = self.decrypter

    def encrypter(self, generator, *a, **kw):
        for i in generator:
            for char in i:
                yield ord(char) + self.num
                yield self.sep

    def decrypter(self, generator, *a, **kw):
        temp = ""
        for i in generator:
            for char in i:
                if char == self.sep:
                    yield chr(temp) - self.num
                    temp = ""
                else:
                    temp += char


class DebugEncrypter(metaclass=DBEXMetaEncrypter):
    gen_encryption = True
    gen_encrypter = None
    gen_decrypter = None

    def __init__(self):
        self.gen_encrypter = self.encrypter
        self.gen_decrypter = self.decrypter

    def encrypter(self, generator, *args, **kwargs):
        for i in generator:
            print(f"enx: {i}")
            for j in i:
                print(f"\t{j}")
                yield j

    def decrypter(self, generator, *args, **kwargs):
        for i in generator:
            print(i, end="")
            yield i
        print("")
