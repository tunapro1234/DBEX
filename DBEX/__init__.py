from dbex.lib.encryption import defaultEncrypter, defaultDecrypter
from dbex.lib.encryption import emptyEncrypter, emptyDecrypter

from dbex.lib.encoder import Encoder as defaultEncoder
from dbex.lib.decoder import Decoder as defaultDecoder

currentEncrypter = emptyEncrypter
currentDecrypter = emptyDecrypter
currentEncoder = defaultEncoder
currentDecoder = defaultDecoder

"                       TO DO:                       "
"""######################################################
# Decoder için gen_lvl 
# Decoder ve Encoderda sort_keys
# Decoder ve Encoder için Exception classları
# Decoder ve Encoder için backslah geliştirmesi
# Biraz daha açıklama koymam çok hoş olabilirdi
# Encoder kısmı Decoder koduna göre çok düzensiz kaçıyor 

######################################################"""


def __Econfigure(cls, encrypter):
    """kullanma"""
    global currentEncoder, currentEncrypter
    encrypter = emptyEncrypter if encrypter is None else encrypter
    currentEncoder = cls if cls is not None else currentEncoder
    currentEncoder.encrypter_func = (currentEncrypter := encrypter)


def __Dconfigure(cls, decrypter):
    """kullanma"""
    global currentDecoder, currentDecrypter
    decrypter = emptyDecrypter if decrypter is None else decrypter
    currentDecoder = cls if cls is not None else currentDecoder
    currentDecoder.decrypter_func = (currentDecrypter := decrypter)


# yapf: disable
def dumps(obj, *args, cls=None, encrypter=currentEncrypter, **kwargs):
    __Econfigure(cls, encrypter)
    return currentEncoder.dumps(obj, *args, **kwargs)

# yapf: disable
def dump(obj, *args, cls=None, encrypter=currentEncrypter, **kwargs):
    __Econfigure(cls, encrypter)
    return currentEncoder.dump(obj, *args, **kwargs)

# yapf: disable
def dumper(obj, *args, cls=None, encrypter=currentEncrypter, **kwargs):
    __Econfigure(cls, encrypter)
    return currentEncoder.dumper(obj, *args, **kwargs)

# yapf: disable
def load(obj, *args, cls=None, decrypter=currentDecrypter, **kwargs):
    """json.load'un çakması

        Args:
            path (str): dosya yolu
            encoding (str): Defaults to "utf-8".

        Returns:
            Dosyada yazılı olan obje
    """
    __Dconfigure(cls, decrypter)
    return currentDecoder.load(obj, *args, **kwargs)

# yapf: disable
def loads(obj, *args, cls=None, decrypter=currentDecrypter, gen_lvl=None, **kwargs):
    """json.loads'un çakması ve generator olabiliyor

        Args:
            string (str): dönüştürülmesi istenen obje
            is_generator (int, optional): Generator olup olmayacağı. Defaults to 0.

        Returns:
            Eğer is_generator True verilirse generator döndüren fonksiyon döndürüyor,
            değilse direkt olarak objenin kendisini döndürüyor
    """
    __Dconfigure(cls, decrypter)
    return currentDecoder.loads(obj, *args, gen_lvl=gen_lvl, **kwargs)

# yapf: disable
def loader(path, *args, cls=None, decrypter=currentDecrypter, **kwargs):
    """[json.load'un generator hali]

    Args:
        path (str): [okunacak dosyanın yolu]
        cls (class): [Decoder classı (elleme)]. Defaults to Decoder from dbex.lib.decoder.
        decrypter (function): [decryption türü]. Defaults to empty_decrypter from dbex.lib.encryption.
        
        encoding (str): Defaults to "utf-8".
        gen_lvl (int, str): [generator objesinin derinliği]. Defaults to "all".

    Returns:
        (Dosyada yazanları döndüren generator) objesi döndüren bir fonksiyon
    """
    __Dconfigure(cls, decrypter)
    return currentDecoder.loader(path, *args, **kwargs)
