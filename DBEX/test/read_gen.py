def read_file(path, encoding="utf-8"):
	char = True
	final = []
	with open(path, encoding=encoding) as file:
		while char:
			final.append((char := file.read(1)))
	return final


def read_file_gen(path):
	char = True
	with open(path, encoding="utf-8") as f:
		while char:
			yield (char := f.read(1))


def write(filename):
	try:
		with open(filename, "a", encoding="utf-8") as f:
			f.write("test için \\\\ \\ \\ \n")
	except:
		return False
	else:
		return True


def test():
	filename = "dbex/res/test.dbex"
	# write(filename)

	# gen = read_file_gen(filename)
	gen = read_file(filename)
	for i in gen:
		print(i, end="")

def test():

 

if __name__ == "__main__":
	test()