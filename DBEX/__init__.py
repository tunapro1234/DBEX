from dbex.lib.encryption import DBEXDefaultEncrypter as DefaultEncryptionClass
from dbex.lib.encryption import DebugEncrypter
from dbex.lib.encoder import Encoder
from dbex.lib.decoder import Decoder

"                       TO DO:                       "
"""######################################################
#	Decoder ve Encoderda sort_keys
#	Encoder dump fonksiyonlarına doc string ekle
#	Biraz daha açıklama koymam çok hoş olabilirdi
#	Decoder ve Encoder için backslash geliştirmesi
#	HATA ISIMLENDIRMELERI
#	
#	Encoder kısmı Decoder koduna göre çok düzensiz kaçıyor 
#		- yoo (gelecekteki tuna)    
#			- yoo öyle (daha da gelecekteki tuna) 
######################################################"""

#   Class oluşturmanız için zorlamayı 
# düşünmüyorum ama documentlara erişim için gerekli olacak

def dump(*args, **kwargs):
	Decoder().dump(*args, **kwargs)

def dumps(*args, **kwargs):
	Decoder().dumps(*args, **kwargs)


def load(*args, **kwargs):
	Encoder().load(*args, **kwargs)

def loads(*args, **kwargs):
	Encoder().loads(*args, **kwargs)

