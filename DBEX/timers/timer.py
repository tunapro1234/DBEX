import dbex.__init__
import json
import time

# Json yaklaşık olarak 5 bin kat daha hızlı
# Bunu Cython kullanarak çözme zamanı

mult = 100
tester = list(range(5))
dumps_tester = [tester] * mult
loads_tester = "[" + f"{tester}, " * (mult - 1) + f"{tester}" + "]"

mult = mult * 5000
tester = list(range(5))
dumps_tester2 = [tester] * mult
loads_tester2 = "[" + f"{tester}, " * (mult - 1) + f"{tester}" + "]"

## json loads
st = time.time()
dbex.loads(loads_tester)
print(endt := time.time() - st)

## dbex loads
st = time.time()
json.loads(loads_tester2)
print(endt2 := time.time() - st)

## dbex dumps
st = time.time()
dbex.dumps(dumps_tester)
print(endt3 := time.time() - st)

## json dumps
st = time.time()
json.dumps(dumps_tester2)
print(endt4 := time.time() - st)

print(f" DBEX loads \t -> {endt}",
      f" JSON loads \t -> {endt2}",
      f" DBEX dumps \t -> {endt3}",
      f" JSON dumps \t -> {endt4}",
      sep="\n")
