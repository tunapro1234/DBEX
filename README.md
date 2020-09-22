# JSON ama generator
Python için olan json kütüphanesinin generator hali.

## Geliştirme aşamasında
Json kütüphanesine yetişebikmem için eklemem gerekn çok fazla özellik var ama maalesef ben 11. sınıfım

### Kullanım
```python
import dbex

defaultSettings = { # çok daha fazla seçenek var
    "default_path": "test.dbex", # yeteri kadar açıklayıcı
    "default_max_depth": 0, # ne kadarı açık olacak (dene gör)
    "default_file_encoding": "utf-8"
}

dec = dbex.Decoder(**defaultSettings)
enc = dbex.Encoder(**defaultSettings)

tester = '["DBEX", "TUNAPRO", [12, [3.4], 5.66], 7, (None), null, {():False, false:true}, Infinity, -Infinity]' # json şeylerini anlıyor

loads = dec.loads(tester) # max_depth parametresiyle oynanmadığı sürüce json ile aynı
result = enc.dumps(loads) # yani hala generator ama döndürmeden önce çeviriyor gibi bir şey

print(f"{tester}\n{result}")
print("ok" if tester == result else "olamaz")
# çalışır herhalde
# umarım
```
#### max_depth Parametresi
`max_depth` parametresi encoder için hangi seviyeye kadar generator olarak devam edeceğini belirliyor, "all" tamamen generator, 0 direkt döndürme.
Decoder için ise hangi seviyeye kadar normal gideceğini söylüyor, belirtilen seviyeden sonrası generator object olarak döndürülüyor. objenin ne olduğuna döndürülen fonksiyon isminden bakılabilir. `tuple_gen`, `list_gen` veya `dict_gen` olabiliyor. bunları işleyen default fonksiyon dec.gen_normalizer, fakat bunları farklı bir şekilde anlamlandırmak isterseniz (tupleları yok etmek gibi) bunu yapabilirsiniz.