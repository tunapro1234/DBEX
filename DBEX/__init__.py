from dbex.lib.encoder import Encoder
from dbex.lib.decoder import Decoder

"                       TO DO:                       "
"""######################################################
#	Decoder ve Encoderda sort_keys
#	Encoder dump fonksiyonlarına doc string ekle
#	Biraz daha açıklama koymam çok hoş olabilirdi
#	Decoder ve Encoder için backslash geliştirmesi
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

def dumper(*args, **kwargs):
	Decoder().dumper(*args, **kwargs)


def load(*args, **kwargs):
	Encoder().load(*args, **kwargs)

def loads(*args, **kwargs):
	Encoder().loads(*args, **kwargs)

def loader(*args, **kwargs):
	Encoder().loader(*args, **kwargs)
