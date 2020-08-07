import time


"""DONE
int-string değerlendirmeleri



""""TODO""""
\ eklenecek
dict tuple düzenlemeleri
ana yapı kısıtlaması
error isimlendirmeleri
print-return yerine raise Exception
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
                part = part.replace(" ", "")
                if part.isdigit():
                    tag = "int#"
                elif part.replace('.', '', 1).isdigit():
                    tag = "float#"
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


def process_(string):    
    tokenizers = "({[\"''\"]})"
    final = tokenize_(string, tokenizers + ":,\\")
    final = tag_(final, tokenizers + ":,\\")
    syntax_check_1_(final, tokenizers)
    
    if final[0].data == "[":
        return init_list(final[1:])
    elif final[0].data == "{":
        return init_dict(final[1:])
    elif final[0].data == "(":
        return init_tuple(final[1:])

    
def init_list(t_list):    
    i = 0
    final = []
    # son kullanılan index
    lui = -1
    # tuple cursorı
    ci = 0
    while i < len(t_list):
        part = t_list[i]
        
        if "token" in part.tags:
            if part.data == "[":            
                if (ci-1) == lui:
                    rv, j = init_list(t_list[i+1:])
                    final.append(rv)
                    lui=ci
                else:
                    print("Syntax Error (,) (Code 004)")
                    return False
                i += j
            
            elif part.data == "(":
                if (ci-1) == lui:
                    rv, j = init_tuple(t_list[i+1:])
                    final.append(rv)
                    lui=ci
                else:
                    print("Syntax Error (,) (Code 004)")
                    return False
                i += j
            
            elif part.data == "{":
                if (ci-1) == lui:
                    rv, j = init_dict(t_list[i+1:])
                    final.append(rv)
                    lui=ci
                else:
                    print("Syntax Error (,) (Code 004)")
                    return False
                i += j
                
            elif part.data == "]":
                return final, i+1
            
            elif part.data == ",":
                ci += 1
            
            elif part.data == ")}":
                print("Syntax Error (Code 005)")
                return False
        
        else:
            if (ci-1) == lui:
                if "str" in part.tags:
                    final.append(part.data)
                elif "int" in part.tags:
                    final.append(int(part.data))
                elif "float" in part.tags:
                    final.append(float(part.data))
                elif "bool" in part.tags:
                    # Kontrolü yukarda bool olarak işaretlerken yapmıştık
                    final.append(True if part.data == "True" else False)
                lui=ci
            else:
                print("Syntax Error (,) (Code 004)")
                return False
        i += 1
    # return final
    return "error"
    
    
# def init_init(t_list, current_index, closing):
#     next_closing = [j for j in range(len(t_list)) if t_list[j].data == closing and j > current_index]
#     if len(next_closing) == 0:
#         print("Syntax Error (Code 003)")
#         return False 
#     next_closing = next_closing[-2]
#     return t_list[(current_index+1):(next_closing+1)], next_closing
    
    
def init_tuple(t_list):
    i = 0
    final = []
    # son kullanılan index
    lui = -1
    # tuple cursorı
    ci = 0
    while i < len(t_list):
        part = t_list[i]
        
        if "token" in part.tags:
            if part.data == "[":            
                if (ci-1) == lui:
                    # a, next_closing = init_init(t_list, i, "]")
                    rv, j = init_list(t_list[i+1:])
                    final.append(rv)
                    lui=ci
                else:
                    print("Syntax Error (,) (Code 004)")
                    return False
                # i = next_closing
                i += j
            
            elif part.data == "(":
                if (ci-1) == lui:
                    # a, next_closing = init_init(t_list, i, ")")
                    rv, j = init_tuple(t_list[i+1:])
                    final.append(rv)
                    lui=ci
                else:
                    print("Syntax Error (,) (Code 004)")
                    return False
                # i = next_closing
                i += j
            
            elif part.data == "{":
                if (ci-1) == lui:
                    # a, next_closing = init_init(t_list, i, "}")
                    rv, j = init_dict(t_list[i+1:])
                    final.append(rv)
                    lui=ci
                else:
                    print("Syntax Error (,) (Code 004)")
                    return False
                # i = next_closing
                i += j
                
            elif part.data == ")":
                return tuple(final), i+1
            
            elif part.data == ",":
                ci += 1

            elif part.data == "]}":
                print("Syntax Error (Code 005)")
                return False
                
        else:
            if (ci-1) == lui:
                if "str" in part.tags:
                    final.append(part.data)
                elif "int" in part.tags:
                    final.append(int(part.data))
                elif "float" in part.tags:
                    final.append(float(part.data))
                elif "bool" in part.tags:
                    # Kontrolü yukarda bool olarak işaretlerken yapmıştık
                    final.append(True if part.data == "True" else False)
                lui=ci
            else:
                print("Syntax Error (,) (Code 004)")
                return False
        i += 1
    return "çok ilginç"
    

def init_dict(t_list):
    raise NotImplementedError


def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(time.time() - start)
    return wrapper

    
@timer
def test():
    tester = "(['tuna((pro)\\''], 1234, ([], ((0)), True, 'False'))"
    # tester = '("tunapro", (()), [[]], [(0, "[\\"]")])'
    # tester = "('tunapro1234', (()), (0, '[\\]'))"
    print(tester)
    rv, _ = process_(tester)
    print(rv)

if __name__ == "__main__":
    test()