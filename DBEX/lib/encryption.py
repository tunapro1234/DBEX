import dbex.res.globalv as gvars

__version__ = gvars.version()

class DBEXDefaultEncrypter:
	def __init__(self):
		gen_encryption = True
		gen_encrypter = self.encrypter
		gen_decrypter = self.decrypter

	def encrypter(generator_func, *args, **kwargs):
		gen = generator_func()
		for i in gen:
			yield i

	def decrypter(generator_func, *args, **kwargs):
		gen = generator_func()
		for i in gen:
			yield i

	# def gen_encrypter(rv, *args, **kwargs):
	# 	return rv

	# def gen_decrypter(rv, *args, **kwargs):
	# 	return rv
