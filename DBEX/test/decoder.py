import types
import time
import json

"""TODO
init_dict
\ geliştirilecek
    It also understands ``NaN``, ``Infinity``, and ``-Infinity`` as
    their corresponding ``float`` values, which is outside the JSON spec.
"""

def tokenize_gen(string, tokenizers="[{(\\,\"')}]"):
    last_index = 0
    active_str = None
    is_string = False
    is_prv_bs = False
    for index, char in enumerate(string):
        new_part = []
        if char in tokenizers:
            if index > (last_index + 1):
                new_part.append("".join(string[(last_index + 1):index]))
            new_part.append(char)
            last_index = index

        elif index == len(string) - 1:
            new_part.append("".join(string[(last_index + 1):]))

        for part in new_part:
            if part in ["'", '"', "\\"]: 
                if part in ["'", '"']:
                    if is_string:
                        is_string = False if is_string == part else is_string
                        if not is_string:
                            active_str.append(part)
                            yield "".join(active_str)
                            active_str = None
                            is_string = False
                        else:
                            active_str.append(part)
                    else:
                        is_string = part
                        active_str = [part]
                elif part == "\\":
                    if is_string:
                        if (is_prv_bs := bool(1 - is_prv_bs)):
                            active_str.append("\\")
                    else:
                        raise Exception("Syntax Error (\\)")
            else:
                if is_string:
                    active_str.append(part)
                else:
                    yield part


def loads(string, is_generator="all"):
    generator = tokenize_gen(string)
    first_element = next(generator)
    
    if first_element in "[({":
        if first_element == "[":
            if is_generator:
                return init_list_gen(generator)
            else:
                init_func = init_list_gen
            
        elif first_element == "{":
            if is_generator:
                return init_dict_gen(generator)
            else:
                init_func = init_dict_gen
        
        elif first_element == "(":
            return tuple(gen_to_list((i for i in init_list_gen(generator, tuple_mode=1))))
        
        return gen_to_list((i for i in init_func(generator)))
            
    else:
        return first_element
    
            
def init_tuple_gen(t_list):
    for i in init_list_gen(t_list, tuple_mode=True):
        yield i
    
                
def init_list_gen(t_gen, tuple_mode=False):
    # son kullanılan index
    lui = -1
    
    # list cursorı
    ci = 0
    
    skip = 0
    next_closing = 0
    closing = ")" if tuple_mode else "]"
    err_closing = "".join([i for i in "]})" if i != closing])
    
    for part in t_gen:
        if part.strip() == "":
            continue
        
        # Eğer tokensa
        if part in "[{(\\,\"')}]":
            # Hangi tür olduğuna göre fonksiyon çağır
            if part in "[{(":
                if part == "[":
                    new_gen = (i for i in init_list_gen(t_gen))

                elif part == "{":
                    new_gen = (i for i in init_dict_(t_gen))

                elif part == "(":
                    new_gen = tuple(gen_to_list((i for i in init_list_gen(t_gen, tuple_mode=1))))

                else:
                    raise Exception("Unknown Error (Code 00-1)")
                
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
            
            elif part == closing:
                break
                            
            elif part == ",":
                ci += 1

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
        # time.sleep(0.5)
    print("]" if not main else "]\n", end="")
    
    
@timer_
def test():
    # 0.016243457794189453
    # tester = "[['tuna((pro)'], 1234, [[], ((0)), None, 'None']]"
    # tester = '("tunapro", (()), [[]], [(0, "[\\"]")])'
    # tester = "('tunapro1234', (()), (0, '[\\]'))"
    # tester = '"a"'
    print(tester)
    print_gen(json.loads(tester))
    

if __name__ == "__main__":
    test()