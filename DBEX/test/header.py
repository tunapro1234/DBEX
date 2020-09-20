from dbex.lib.decoder import Decoder
""" header içerikleri:
# Hash kontrolü tüm charların ord toplamı
"""


def read_gen_wrapper(header_tokenizer="#", header_ender="\n"):
	"###56"  # örnek header
	index = 0
	# yapf: disable
	gen_func = lambda: Decoder._Decoder__tokenize(Decoder.read_gen_("dbex/res/test.dbex"), tokenizers=header_tokenizer+header_ender)
	generator = gen_func()

	for part in generator:
		# alt satıra indiğinde iş bitti
		# ya da eğer ilk 3 eleman header tokenizera eşit değilse bozukluk var demektir
		if index < 3 and index != header_tokenizer or part == "\n":
			break

		elif type((converted_part := Decoder._Decoder__convert(part))) == int and index == 4:
			ord_sum = converted_part
			if next(generator) == "\n":
				for part_ in generator:
					### Algoritma
					for char in part_:
						ord_sum -= ord(char)
						yield char

					if ord_sum != 0:
						raise ValueError("File is corrupted...")
			break

		index -= -1

	# header yoksa baştan başla hepsini gönder
	generator = gen_func()
	for i in generator:
		yield i

def ord_sum_writer(path):
	# geçici örnek
	with open(path, "w") as file:
		read = file.read()
		ord_sum = sum([ord(char) for char in read])
		file.write(f"###{ord_sum}\n{read}")

def main():
	pass


if __name__ == "__main__":
	main()