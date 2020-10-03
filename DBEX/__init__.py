# from dbex.encryption import ExampleEncrypter1 as DefaultEncryptionClass
from dbex.encoder import Encoder
from dbex.decoder import Decoder
import dbex.encryption
"""## TO DO ######################################################
#	
#	HEADER
#	Encoder dump fonksiyonlarına doc string ekle
#	Biraz daha açıklama koymam çok hoş olabilirdi
#	Decoder ve Encoder için backslash geliştirmesi
#	
#	WRITE_GEN için file parametresi eklenebilir (gerek var mı?)
#	HATA ISIMLENDIRMELERI
#	
#	
#	## Boş
#	Encoder kısmı Decoder koduna göre çok düzensiz kaçıyor
#	    - yoo (gelecekteki tuna)
#	        - yoo öyle (daha da gelecekteki tuna)
#	
#	Decoder ve Encoderda sort_keys geliştirilebilir
#	Decoder kodu en az 4 kere dosyayı baştan okuyor ona bi el at
#	    - muhtemelen bir şey yapamam
#	
###################################################### TO DO ##"""

#   Class oluşturmanız için zorlamayı
# düşünmüyorum ama documentlara erişim için gerekli olacak


def dump(*a, **kw):
    return Encoder().dump(*a, **kw)


def dumps(*a, **kw):
    return Encoder().dumps(*a, **kw)


def load(*a, **kw):
    return Decoder().load(*a, **kw)


def loads(*a, **kw):
    return Decoder().loads(*a, **kw)
