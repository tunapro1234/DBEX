import types
import time
import json

"""TODO
init_dict
\ geliştirilecek
tokenize ve tag fonksiyonlarını generatora çevir
    It also understands ``NaN``, ``Infinity``, and ``-Infinity`` as
    their corresponding ``float`` values, which is outside the JSON spec.
"""

def tokenize_(string, tokenizers, settings=None, banned_chars=None):
    # girdilerin doğruluğu kontrol ediliyor
    try:
        if type(tokenizers[0]) != str or type(string[0]) != str: 
            raise Exception("")
    except:
        print("Tokenizer input error")
        return False

    final = []
    last_index = 0
    # final = [string[:indexes[0]]]
    for index, char in enumerate(string):
        # ayıklanması istenen karakterlerden birine denk gelindiğinde
        if char in tokenizers:
            # last_index değişkeni ile ayıklancak karakter arasını ekle
            final.append(string[(last_index + 1):index])
            # ayıklanacak karakteri ekle
            final.append(char)
            # last_index değişkenini yenile
            last_index = index

        # Son elemandaysak ve eklenen son şey
        # bize verilen stringin son elemanı değilse
        elif index == len(string) - 1: # and last_index == index:
            # en son bulunan tokendan sonrasını da ekle
            final.append(string[(last_index + 1):])
        
        # ilk başta çıkarılması istenen karakterlerden biri varsa final arrayinin 
        # ilk elemanı "" oluyordu onu engellemek için alttaki list comprehension var
    final = [j for i, j in enumerate(final) if j != ""] # and i != 0 
    
    # istenmeyen karakter belirtildiyse
    if banned_chars is not None:
        banned_final = []
        # arrayin içindeki her parçanın her karakteri için
        for part in final:
            # istenmeyen karakter olup olmadığını kontrol edip istenenleri yeni değişkene ekle
            banned_final.append("".join([char for char in part if not char in banned_chars]))
        final = banned_final
        
    return final


def tag_(arr, tokenizers):
    class Part:
        def __init__(self, data, tags):
            self.data = data
            self.tags = tags

        def __str__(self):
                return "DATA: " + str(self.data) + " ### TAGS: " + str(self.tags)
    
    final = []
    is_string = False
    for part in arr:
        if part in tokenizers:
            if part == "'" or part == '"':
                # Eğer önceki parça \ ise token sayılmayacak
                if len(final) > 0 and "bs" in final[-1].tags:
                    # önceki backslash str şu anki parça haline geliyor ve şu anki geçiliyor
                    final[-1].data = part
                    final[-1].tags = "str#"
                    tag = "ignore#"
                else:
                    is_string = bool(1 - is_string)
                    tag = "ignore#"
                    # tag = "token#"
            elif not is_string:
                if part == "\\": 
                    print("Syntax Error (\\) (Code 000)")
                    return False
                tag = "token#"
            else:
                # önümüze \ geldiyse ve string içindeysek
                if part == "\\":
                    # eğer önceki eleman da \ ise şu anki \ str olacak
                    if len(final) > 0 and "bs" in final[-1].tags:
                        # önceki backslash str haline getiriliyor ve şu anki geçiliyor
                        final[-1].tags = "str#"
                        tag = "ignore#"
                    # değilse özel token olarak devam
                    else:
                        # öncesinde backslash yoksa işaretleyip devam
                        tag = "bs#"
                # normal str işte
                else:
                    tag = "str#"
        else:
            if is_string:
                tag = "str#"
            else:
                # part = part.replace(" ", "")
                part = part.strip()
                if part.isdigit():
                    tag = "int#"
                elif part.replace('.', '', 1).isdigit():
                    tag = "float#"
                elif part in ["None"]:
                    tag = "none#"
                elif part in ["True", "False"]:
                    tag = "bool#"
                elif part == "":
                    tag = "ignore#"
                else:
                    print("Syntax Error (Code 001)")
                    return False
        if tag != "ignore#":
            final.append(Part(part, tag))
    
    #region Aslında string olan tokenları stringle birleştirme
    prev_tag = ""
    new_final = []
    for part in final:            
        # \ olayı cidden sinir bozucu
        if "bs" in part.tags:
            part.tags = "str#"
            # print(len(part.data))
            
        if prev_tag == part.tags and "str" in part.tags:
            new_final[-1].data += part.data
        else:
            new_final.append(part)
            prev_tag = part.tags
    final = new_final
    #endregion #########################################    
    return final


def syntax_check_1_(arr, tokenizers):
    #   Parantez ve tırnak gibi şeylerin açılma ve 
    # kapanma sayılarının aynı olup olmadığının kontrolü
    comp = [part.data for part in arr if "token" in part.tags]
    
    a = [i for i in comp if i in tokenizers[:len(tokenizers)//2]]
    b = [j for j in comp if j in tokenizers[(len(tokenizers)//2):]]
    if len(a) != len(b):
        print("Syntax Error (Code 002)")
        return False 
    a, b = None, None
    return True


def loads(string, generator="all"):
    tokenizers = "({[\"''\"]})"
    final = tokenize_(string, tokenizers + ":,\\")
    final = tag_(final, tokenizers + ":,\\")
    syntax_check_1_(final, tokenizers)
    
    if final[0].data in "[({":
        if final[0].data == "[":
            if generator:
                return init_list_gen(final[1:])
            else:
                init_func = init_list_gen
            
        elif final[0].data == "{":
            if generator:
                return init_dict_gen(final[1:])
            else:
                init_func = init_dict_gen
        
        elif final[0].data == "(":
            # if generator:
            #     return init_list_gen(final[1:], tuple_mode=1)
            # else:
            
            # (tuple için generatorı kapattım)
            return tuple(gen_to_list((i for i in init_list_gen(final[1:], tuple_mode=1))))
        
        return gen_to_list((i for i in init_func(final[1:])))
            
    elif len(final) == 1:
        return final[0].data
    
    
def find_next_closing(arr, index, type):
    cot = 1
    for i in range(index+1, len(arr)):      
        if arr[i].data == type[0]:
            cot += 1
        elif arr[i].data == type[1]:
            cot -= 1
        
        if cot == 0:
            return i
            
            
def init_tuple_gen(t_list):
    for i in init_list_gen(t_list, tuple_mode=True):
        yield i
    
                
def init_list_gen(t_list, tuple_mode=False):
    # son kullanılan index
    lui = -1
    
    # list cursorı
    ci = 0
    
    skip = 0
    next_closing = 0
    closing = ")" if tuple_mode else "]"
    err_closing = "".join([i for i in "]})" if i != closing])
    
    for index, part in enumerate(t_list):
        # İmlecin üzerinde olduğu parça
        
        # Atlama şeyini yaptım bir daha while kullanmam
        if skip:
            if skip == index:
                next_closing = skip = False
            else:
                continue
        # Geri gitme olmadığını fark ettim. while mükemmel
        
        # Eğer tokensa
        # if part in "[{(,)}]":
        if "token" in part.tags:
            # Hangi tür olduğuna göre fonksiyon çağır
            if part.data in "[{(":
                if part.data == "[":
                    next_closing = find_next_closing(t_list, index, "[]")
                    new_gen = (i for i in init_list_gen(t_list[(index+1):next_closing]))

                elif part.data == "{":
                    next_closing = find_next_closing(t_list, index, "{}")
                    new_gen = (i for i in init_dict_(t_list[(index+1):next_closing]))

                elif part.data == "(":
                    next_closing = find_next_closing(t_list, index, "()")
                    new_gen = tuple(gen_to_list((i for i in init_list_gen(t_list[(index+1):next_closing], tuple_mode=1))))

                else:
                    raise Exception("Unknown Error (Code 00-1)")
                
                skip = (next_closing+1)
                
                if (ci-1) == lui:
                    # Buralar çok değişti en son yazmak en mantıklısıymış
                    yield new_gen
                    
                    #   ve içinde bulunduğumuz listenin
                    # kullandığımız indexinin kullanılmış olduğunu belirtiyoruz
                    lui=ci
                    # ki virgül koymadan yeni bir indexe atlamasın
                    # işte virgül koyunca ci yi bir arttırıyoruz sonra ikisi farklı oluyor filan
                    
                else:
                    # virgül koymadan yeni eleman eklenemiyor
                    raise Exception("Syntax Error (,) (Code 004)")
                # Yukarda dediğim atlama
                # Diğerleri de aynı işte
                # index += j
            
            elif part.data == closing:
                break
                            
            elif part.data == ",":
                ci += 1

            elif part.data in err_closing:
                # Yanlış kapatma 
                raise Exception("Syntax Error (]}) (Code 005)")
                # Zaten kesin daha önce syntax error döndürür
                
        # Aktif parça token değilse
        else:
            # Virgül koyulup yeni yer açılmışsa
            if (ci-1) == lui:
                # ekle işte
                if "none" in part.tags:
                    yield None
                elif "str" in part.tags:
                    yield part.data
                elif "int" in part.tags:
                    yield int(part.data)
                elif "float" in part.tags:
                    yield float(part.data)
                elif "bool" in part.tags:
                    # Kontrolü yukarda bool olarak işaretlerken yapmıştık
                    yield True if part.data == "True" else False
                    # tag_ fonksiyonunda olması lazım
                else:
                    raise Exception("Syntax Error (Code 006)")
                # luici kesinlikle kasıtlı değildi
                lui=ci
                # Yukarda demiştim zaten işte
                # Kullanıldığını belirtme filan
            else:
                # lui ile ci farklı olmazsa virgül koyulmadıüını anlıyor
                raise Exception("Syntax Error (,) (Code 004)")
        

def init_dict(t_list):
    # Muhtemelen bunu yazamayacağım
    raise NotImplementedError


#   ilk baştaki mal tokenizing algoritmamda sorting 
# metodunu değiştirmenin ne kadar etkileyecğini görmek içindi
def timer_(func):
    # Güzel özellik 
    def wrapper():
        start = time.time()
        func()
        print(time.time() - start)
    return wrapper
    
    
def gen_to_list(gen):
    final = []
    for i in gen:
        if isinstance(i, types.GeneratorType):
            final.append(gen_to_list(i))
        else:
            final.append(i)
    return final
    

def print_gen(gen, main=True):
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
        time.sleep(0.5)
    print("]" if not main else "]\n", end="")
    
    
@timer_
def test():
    # 0.016243457794189453
    tester = "[['tuna((pro)\\''], 1234, [[], ((0)), None, 'None']]"
    # tester = '("tunapro", (()), [[]], [(0, "[\\"]")])'
    # tester = "('tunapro1234', (()), (0, '[\\]'))"
    # tester = '"a"'
    print(tester)
    print_gen(loads(tester, generator=1))
    

if __name__ == "__main__":
    test()