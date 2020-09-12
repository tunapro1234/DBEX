from dbex.lib.encrypt import encrypter as defaultEncrypter
from dbex.lib.encrypt import decrypter as defaultDecrypter

from dbex.lib.encoder import Encoder as defaultEncoder
from dbex.lib.decoder import Decoder as defaultDecoder

currentEncrypter = defaultEncrypter
currentDecrypter = defaultDecrypter
currentEncoder = defaultEncoder
currentDecoder = defaultDecoder

#   Tüm fonksiyonlar birbirini gereksiz
# fazla tekrar ediyor çok rahatsız edici


# yapf: disable
def dumps(obj, *args, cls=None, encrypter=currentEncrypter, **kwargs):
    global currentEncoder, currentEncrypter
    # Encrypter parametresine none değeri verilince boş bir fonksiyon veriliyor
    encrypter = lambda rv, *args, **kwargs: rv if encrypter is None else encrypter
    currentEncoder = cls if cls is not None else currentEncoder
    currentEncoder.encrypter = (currentEncrypter := encrypter)
    return currentEncoder.dumps(obj, *args, **kwargs)

# yapf: disable
def dump(obj, *args, cls=None, encrypter=currentEncrypter, **kwargs):
    global currentEncoder, currentEncrypter
    # Encrypter parametresine none değeri verilince boş bir fonksiyon veriliyor
    encrypter = lambda rv, *args, **kwargs: rv if encrypter is None else encrypter
    currentEncoder = cls if cls is not None else currentEncoder
    currentEncoder.encrypter = (currentEncrypter := encrypter)
    return currentEncoder.dump(obj, *args, **kwargs)

# yapf: disable
def dumper(obj, *args, cls=None, encrypter=currentEncrypter, **kwargs):
    global currentEncoder, currentEncrypter
    # Encrypter parametresine none değeri verilince boş bir fonksiyon veriliyor
    encrypter = lambda rv, *args, **kwargs: rv if encrypter is None else encrypter
    currentEncoder = cls if cls is not None else currentEncoder
    currentEncoder.encrypter = (currentEncrypter := encrypter)
    return currentEncoder.dumper(obj, *args, **kwargs)

# yapf: disable
def loads(obj, *args, cls=None, decrypter=currentDecrypter, **kwargs):
    global currentDecoder, currentDecrypter
    # Decrypter parametresine none değeri verilince boş bir fonksiyon veriliyor
    decrypter = lambda rv, *args, **kwargs: rv if decrypter is None else decrypter
    currentDecoder = cls if cls is not None else currentDecoder # decoder classı belirlenmesi
    currentDecoder.decrypter = (currentDecrypter := decrypter)
    return currentDecoder.loads(obj, *args, **kwargs)

# yapf: disable
def load(obj, *args, cls=None, decrypter=currentDecrypter, **kwargs):
    global currentDecoder, currentDecrypter
    # Decrypter parametresine none değeri verilince boş bir fonksiyon veriliyor
    decrypter = lambda rv, *args, **kwargs: rv if decrypter is None else decrypter
    currentDecoder = cls if cls is not None else currentDecoder # decoder classı belirlenmesi
    currentDecoder.decrypter = (currentDecrypter := decrypter)
    return currentDecoder.load(obj, *args, **kwargs)

# yapf: disable
def loader(obj, *args, cls=None, decrypter=currentDecrypter, **kwargs):
    global currentDecoder, currentDecrypter
    # Decrypter parametresine none değeri verilince boş bir fonksiyon veriliyor
    decrypter = lambda rv, *args, **kwargs: rv if decrypter is None else decrypter
    currentDecoder = cls if cls is not None else currentDecoder # decoder classı belirlenmesi
    currentDecoder.decrypter = (currentDecrypter := decrypter)
    return currentDecoder.loader(obj, *args, **kwargs)
