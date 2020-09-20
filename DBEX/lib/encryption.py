def version():
	with open("dbex/res/VERSION.txt") as file:
		return file.read()


__version__ = version()


def encrypter(rv, *args, **kwargs):
	return rv


def decrypter(rv, *args, **kwargs):
	return rv


def empty_encrypter(rv, *args, **kwargs):
	return rv


def empty_decrypter(rv, *args, **kwargs):
	return rv


emptyEncrypter = empty_encrypter
emptyDecrypter = empty_decrypter
defaultEncrypter = encrypter
defaultDecrypter = decrypter