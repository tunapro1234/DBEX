import types
import time
import json

"""TODO
init_dict
\ geliştirilecek
generator levels
    It also understands ``NaN``, ``Infinity``, and ``-Infinity`` as
    their corresponding ``float`` values, which is outside the JSON spec.
"""


def read_file_gen(path, encoding="utf-8"):
    #   Dosyanın sonuna gelmediğimiz 
    # sürece sonraki elemanı okuyup yolla
    char = True
    with open(path, encoding=encoding) as f:
        while char:
            yield (char := f.read(1))


def read_file(path, encoding="utf-8"):
    # Hepsini oku yolla
    with open(path, encoding=encoding) as f:
        return f.read()
    # neden var bilmiyorum


def tokenize_(string, tokenizers="[{(\\,\"')}]"):
    # Sonraki bölüme vermek için böyle bir değişken var
    # Direkt olarak ayrı bir fonksiyon halinde bıraksaydım daha hoş olurdu
    # Haha yaptım
    # ve artık o değişken yok :-(
    
    # Son token indexi 
    temp = ""
    last_token_index = 0
    ending_index = 0
    #   Ki bir daha token bulduğumzda eskisi 
    # ile yeni bulunan arasını da yollayabilelim
    
    for index, char in enumerate(string):
        if char in tokenizers:
            # "" önlemek için
            if index > (last_token_index + 1):
                # son token ile şu anki token arasını yolla
                yield temp
                # yield "".join(string[(last_token_index + 1):index])
            # tokenın kendinsini yolla
            yield char
            temp = ""
            # son token şimdiki token
            last_token_index = index
    
        # Ben malım
        # elif index == len(string) - 1:
            # Sondan bir önceki karakter token değilse 
            # yield "".join(string[(last_index + 1):])
            # Son tokendan sonuna kadar yolla
        # generatorde sondan bir öncekini nası anlıcan
        # Bunu yarın geliştiriyoruz sonra dict
        
        # between tarzı değişken yap
        
        else:
            temp += char
        
        ending_index = index
    
    if ending_index != last_token_index:
        yield temp


def tokenize_gen(reader_gen, tokenizers="[{(\\,\"')}]"):
    #   eğer tırnak işaret ile string değer 
    # girilmeye başlanmışsa değerlerin kaydolacağı liste
    active_str = None
    # Hangi tırnak işaretiyle başladığımız
    is_string = False
    # Önceki elemanın \ olup olmadığı
    is_prv_bs = False
    
    for part in tokenize_(reader_gen, tokenizers):
        if part in ["'", '"', "\\"]: 
            # Parça tırnak işaretiyse
            if part in ["'", '"']:
                # String içine zaten girdiysek
                if is_string:
                    #       Eğer stringi açmak için kullanılan tırnak 
                    #   işaretiyle şu an gelen tırnak işareti 
                    # aynıysa string kapatılıyor (is_string False oluyor)
                    is_string = False if is_string == part else is_string
                    
                    # Eğer string şimdi kapatıldıysa
                    if not is_string:
                        # Son parçayı aktif stringe ekle
                        active_str.append(part)
                        
                        # Aktif stringi birleştirip yolla
                        yield "".join(active_str)
                        # Bu noktada neden aktif stringi listede topladığımı sorgulamaya başlıyorum
                        
                        # Sıfırla
                        active_str = None
                        is_string = False

                    # Hala stringin içindeysek
                    else:
                        # Parçayı ekle
                        active_str.append(part)
                        # Diğer tırnak işareti olması ve \ için
                
                # String içine daha yeni giriyorsak
                else:
                    # Hangi tırnakla girdiğimizi belirt
                    is_string = part
                    # Tırnağı aktif stringe ekle
                    active_str = [part]
                    
                    #   aktif stringe tırnak ekleme sebebim ileride 
                    # string ve int değerlerin ayrımını kolaylaştırmak
                    
                    #   İlk başta .tags ve .data şeylerine sahip 
                    # olan bir class açmıştım ama şu an gereksiz görüyorum
            
            elif part == "\\":
                # Lanet olası şey
                if is_string:
                    # Önceki bu değilse anlam kazansın
                    # Buysa anlamını yitirisin (\\ girip \ yazması için filan) 
                    is_prv_bs = bool(1 - is_prv_bs)
                    active_str.append("\\")

                    # oysa ki seni kullanmayı çok isterdim
                    # if (is_prv_bs := bool(1 - is_prv_bs)):
                    #     active_str.append("\\")
                else:
                    # String dışında kullanmak yasak
                    raise Exception("Syntax Error (\\)")
                    # Karakter karakter okuduğum için satır sonlarında (\n) umarım sıkıntı çıkarmaz
        
        else:
            # Stringse ekle değilse yolla
            if is_string:
                active_str.append(part)
            else:
                yield part


def init_list_gen(t_gen, tuple_mode=False):
    # son kullanılan index
    lui = -1
    
    # list cursorı
    ci = 0
    
    # Parantez kapatma değişkeni
    closing = ")" if tuple_mode else "]"
    # İstemediğimiz parantez kapatma şekilleri
    err_closing = "".join([i for i in "]})" if i != closing])
    
    for part in t_gen:
        # string içinde olmayan boşluk gelirse geç
        if part.strip() == "":
            # Bunu üsteki fonksiyonlarda çözmem daha hoş olurdu
            continue
        
        # Eğer tokensa
        if part in "[{(\\,\"')}]":
            # Buralar çok değişti en son yazmak en mantıklısıymış
            # Hangi tür olduğuna göre fonksiyon çağır
            if part in "[{(":
                if (ci-1) == lui:
                    if part == "[":
                        # Generator recursion
                        yield (i for i in init_list_gen(t_gen))
                        # Burda ufak bir hata yakaladım
                        
                        #                           Fonksiyonun normal kullanımı halinde herhangi bir sıkıntı 
                        #                       oluşmamasına rağmen eğer döndürdüğü generator objesini tamamen 
                        #                   tüketmeden daha fazla değer almaya çalışırsanız imleç, döndürdüğüm    
                        #               generatorun gitmesi gereken yerlerden gidiyor, bu da 1 milyon hataya 
                        #           sebep oluyor. Çözüm olarak generator levelleri koymak istiyorum örnek 
                        #       olarak generator = 1 olduğunda sadece en üst katmandaki değerler generator 
                        #   olarak döndürülecek. Yorum satırlarına kodlardan daha çok zaman harcamak beni 
                        # çok rahatsız ediyor. Bu cümleyle bu güzel yorumu daha da mükemmelleştiriyorum.
                        
                        #       Bunu çözmek için döndüreceğimiz generatorlara farklı generator verebiliriz.
                        #   Bu da sonraki parantezi bulmak ve imleci oraya atlatmak gibi eski fonksiyonları 
                        # çıkarmam gerektiği anlamına geliyor. Muhtemelen bir ara hallederim ama önce dict.

                        
                    elif part == "{":
                        yield (i for i in init_dict_(t_gen))

                    elif part == "(":
                        # Tuple objeler generator olarak işlenmiyor 
                        yield tuple(gen_to_list((i for i in init_list_gen(t_gen, tuple_mode=1))))
                        #   tuple.append olmadığı için yapmama rağmen generator olan ve 
                        # olmaya objelere daha iyi hakim olmamızı sağlayacak gibi görünüyor
                    else:
                        raise Exception("Unknown Error (Code 00-1)")
                    
                    # last used index -> lui
                    # current index -> ci
                    
                    #   İçinde bulunduğumuz listenin
                    # kullandığımız indexinin kullanılmış olduğunu belirtiyoruz
                    lui=ci
                    #   ki virgül koymadan yeni bir indexe atlamasın
                    # işte virgül koyunca ci yi bir arttırıyoruz sonra ikisi farklı oluyor filan
                    
                else:
                    # virgül koymadan yeni eleman eklenemiyor
                    raise Exception("Syntax Error (,) (Code 004)")
                
            elif part == closing:
                # kapatıyorsan kapat
                break
                            
            elif part == ",":
                # Current indexi arttır ki 
                ci += 1
                # son kullanılmış olanla aynı olmasın

            elif part in err_closing:
                # Yanlış kapatma 
                raise Exception("Syntax Error (]}) (Code 005)")
                # Zaten kesin daha önce syntax error döndürür
                
        # Aktif parça token değilse
        else:
            # Virgül koyulup yeni yer açılmışsa
            if (ci-1) == lui:
                # ekle işte
                part = part.strip()
                # None
                if part in ["None", "null"]:
                    yield None
                # String
                elif part[0] in "\"'" and part[-1] in "\"'":
                    yield part[1:-1]
                # Integer
                elif part.isdigit():
                    yield int(part)
                # Float
                elif part.replace('.', '', 1).isdigit():
                    yield float(part)
                # Boolean
                elif part in ["True", "true", "False", "false"]:
                    # Şimdilik JSON uyumlu olsun hadi
                    yield True if part in ["True", "true"] else False
                else:
                    raise Exception("Syntax Error (Code 006)")
                # luici kesinlikle kasıtlı değildi
                lui=ci
                # Yukarda demiştim zaten işte
                # Kullanıldığını belirtme filan
            else:
                # lui ile ci farklı olmazsa virgül koyulmadığını anlıyor
                raise Exception("Syntax Error (,) (Code 004)")


def init_dict(t_list):
    # Muhtemelen bunu yazamayacağım
    raise NotImplementedError


def load_(generator, is_generator="all"):
    # generatorın türü farklı olabileceği için küçük bir şeyler
    # first_element = next(generator) if isinstance(generator, types.GeneratorType) else generator[0]
    # olmayacağını fark ettim
    
    first_element = next(generator)
    
    # İlk eleman işlememiz gereken bir şeyse
    # Ne olduğuna göre işleyicileri çağır
    if first_element == "[":
        if is_generator:
            # Generatorsa generatoru döndür
            return init_list_gen(generator)
        else:
            # Değilse generatordan listeye dönüştürülecek elemanı döndür
            return gen_to_list((i for i in init_list_gen(generator)))
            init_func = init_list_gen
        
    elif first_element == "{":
        if is_generator:
            return init_dict_gen(generator)
        else:
            init_func = init_dict_gen
    
    elif first_element == "(":
        # Tuple objeler için generator özelliği kapalı
        return tuple(gen_to_list((i for i in init_list_gen(generator, tuple_mode=1))))
            
    else:
        # Burda da biraz patlak veriyoruz
        # off bunu sabah yazmıştım nerde patlak verdiğimizi unuttum
        return first_element


def load(path, is_generator="all", encoding="utf-8"):
    # Bunu anlatmayacağım
    generator = tokenize_gen(read_file_gen(path, encoding=encoding))
    return load_(generator, is_generator)
    
    
def loads(string, is_generator="all"):
    # Bunu da
    generator = tokenize_gen(string)
    return load_(generator, is_generator)
    
    
def gen_to_list(gen):
    final = []
    for i in gen:
        if isinstance(i, types.GeneratorType):
            final.append(gen_to_list(i))
        else:
            final.append(i)
    return final
    

def print_gen(gen, main=True):
    if isinstance(gen, types.GeneratorType):
        print("[", end="")
        for i in gen:
            if isinstance(i, types.GeneratorType):
                print_gen(i, main=False)
            else:
                if type(i) == str:
                    print("\"" + i + "\"", end="")
                else:
                    print(i, end="")
                    
            print(", ", end="")
            time.sleep(0.3)
        print("]" if not main else "]\n", end="")
    else:
        print(gen)

def timer_(func):
    #   ilk baştaki mal tokenizing algoritmamda sorting 
    # metodunu değiştirmenin ne kadar etkileyecğini görmek içindi
    def wrapper():
        # Güzel özellik 
        start = time.time()
        func()
        print(time.time() - start)
    return wrapper
    
    
@timer_
def test():
    # tester = "[['tuna((pro)'], 1234, [[], ((0)), None, 'None']]"
    # tester = "('tunapro1234', (()), (0, '[\\]'))"
    # tester = '("tunapro", (()), [[]], [(0, "[\\"]")])'

    tester = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
    # tester = '1234'
    print(tester)
    print(loads(tester, is_generator=False))
    
    # BÜYÜK HATA
    # for i in loads(tester):
    #     print(str(i))
    

if __name__ == "__main__":
    test()