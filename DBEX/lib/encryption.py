import dbex.res.globalv as gvars

__version__ = gvars.version()

class DBEXDefaultEncrypter:
	def __init__(self):
		self.gen_encryption = True
		self.gen_encrypter = self.encrypter
		self.gen_decrypter = self.decrypter

	def encrypter(self, generator, *args, **kwargs):
		for i in generator:
			yield i

	def decrypter(self, generator, *args, **kwargs):
		for i in generator:
			yield i

class DebugEncrypter:
	def __init__(self):
		self.gen_encrypter = self.encrypter
		self.gen_decrypter = self.decrypter
		self.gen_encryption = True

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

