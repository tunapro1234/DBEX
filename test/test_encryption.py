from dbex.__init__ import DebugEncrypter
from dbex.__init__ import Decoder  # sonunda
from dbex.__init__ import Encoder
import unittest
import os

enc, dec = Encoder(), Decoder()


class TestEncryption(unittest.TestCase):
    test_file = "dbex/test/TestEncryption.dbex"

    def setUp(self):
        with open(self.test_file, "w+") as file:
            file.write("")

    def tearDown(self):
        os.remove(self.test_file)

    def test_encryption(self):
        kwargs = {"path": self.test_file, "encryption_obj": EmptyEncrypter()}
        enc1 = Encoder(**kwargs)
        dec1 = Decoder(**kwargs)

        tester = []
        enc1.dump(tester)
        read = dec1.load()

        self.assertEqual(tester, read)

    def test_encryption_debug(self):
        kwargs = {"path": self.test_file, "encryption_obj": DebugEncrypter()}
        enc1 = Encoder(**kwargs)
        dec1 = Decoder(**kwargs)

        tester = ["deneme", 123]
        enc1.dump(tester, max_depth="all")
        read = dec1.load()

        self.assertEqual(tester, read)

    def test_encrypter1_dump_load(self):
        kwargs = {
            "path": self.test_file,
            "encryption_obj": TestEncrypter1("3")
        }
        enc1 = Encoder(**kwargs)
        dec1 = Decoder(**kwargs)

        tester = ["deneme", 123]
        enc1.dump(tester, max_depth="all")
        read = dec1.load()

        self.assertEqual(tester, read)

    def test_encrypter1_dumps_loads(self):
        kwargs = {
            "path": self.test_file,
            "encryption_obj": TestEncrypter1("3")
        }
        enc1 = Encoder(**kwargs)
        dec1 = Decoder(**kwargs)

        tester = ["deneme", 123]
        result = dec1.loads(enc1.dumps(tester))

        self.assertEqual(tester, result)

    def test_encrypter1_1(self):
        tester = "['deneme', 123]"
        enx = TestEncrypter1("3")

        for i in enx.encrypter(tester):
            print(i, end="")

        encrypted = "".join([i for i in enx.encrypter(tester)])
        decrypted = "".join([i for i in enx.decrypter(encrypted)])

        self.assertEqual(decrypted, tester)


class EmptyEncrypter:
    def __init__(self):
        self.gen_encrypter = self.encrypter
        self.gen_decrypter = self.decrypter
        self.gen_encryption = True

    def encrypter(self, generator, *args, **kwargs):
        for i in generator:
            yield i

    def decrypter(self, generator, *args, **kwargs):
        for i in generator:
            yield i


class TestEncrypter1:
    def __init__(self, password=None, sep="."):
        self.password = password if password is not None else None
        self.gen_decrypter = self.decrypter
        self.gen_encrypter = self.encrypter
        self.gen_encryption = True
        self.sep = sep

    def encrypter(self, generator, *args, **kwargs):
        self.password = kwargs[
            "password"] if self.password is None else self.password

        for i in generator:
            for char in i:
                yield str(ord(char) + int(str(self.password)[0]))
                yield self.sep

    def decrypter(self, generator, *args, **kwargs):
        self.password = kwargs[
            "password"] if self.password is None else self.password

        temp = ""
        for i in generator:
            for char in i:
                if char == self.sep:
                    yield chr(int(temp) - int(str(self.password)[0]))
                    temp = ""

                else:
                    temp += char
