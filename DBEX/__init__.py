from dbex.lib.encryption import ExampleEncrypter1 as DefaultEncryptionClass
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
#	
#	Decoder kodu en az 4 kere dosyayı baştan okuyor ona bi el at
######################################################"""

#   Class oluşturmanız için zorlamayı
# düşünmüyorum ama documentlara erişim için gerekli olacak


def dump(*a, **kw):
    Decoder().dump(*a, **kw)


def dumps(*a, **kw):
    Decoder().dumps(*a, **kw)


def load(*a, **kw):
    Encoder().load(*a, **kw)


def loads(*a, **kw):
    Encoder().loads(*a, **kw)
