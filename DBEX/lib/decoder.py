import types
import time
import json

"""TODO
\ geliştirilecek
"""

class Decoder:
    @staticmethod
    def _tokenize(string, tokenizers="[{(\\,:\"')}]"):
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
                # tokenın kendinsini yolla
                yield char
                temp = ""
                # son token şimdiki token
                last_token_index = index
        
            else:
                temp += char
            ending_index = index
        if ending_index != last_token_index:
            yield temp

    @staticmethod
    def _tokenize_gen(reader_gen, tokenizers="[{(\\,:\"')}]"):
        #   eğer tırnak işaret ile string değer 
        # girilmeye başlanmışsa değerlerin kaydolacağı liste
        active_str = None
        # Hangi tırnak işaretiyle başladığımız
        is_string = False
        # Önceki elemanın \ olup olmadığı
        is_prv_bs = False
        
        for part in Decoder._tokenize(reader_gen, tokenizers):
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
                
                elif part.strip() != "":
                    yield part

    @staticmethod
    def _init_list_gen(t_gen_func, tuple_mode=False):
        t_gen = t_gen_func()
        # son kullanılan index
        lui = -1
        
        # list cursorı
        ci = 0
        
        # Parantez kapatma değişkeni
        closing = ")" if tuple_mode else "]"
        # İstemediğimiz parantez kapatma şekilleri
        err_closing = "".join([i for i in "]})" if i != closing])
        
        index = -1
        for part in t_gen:
            index += 1
            # Eğer tokensa
            if part in "[{(\\,:\"')}]":
                # Buralar çok değişti en son yazmak en mantıklısıymış
                # Hangi tür olduğuna göre fonksiyon çağır
                if part in "[{(":
                    if (ci-1) == lui:
                        if part == "[":
                            next_closing = Decoder._find_next_closing(t_gen, index, "[]")
                            new_gen_func = lambda: (j for i, j in enumerate(t_gen_func()) if index < i <= next_closing)
                            
                            def list_gen():
                                return (i for i in Decoder._init_list_gen(new_gen_func))
                            yield list_gen
                            index = next_closing
                            
                        elif part == "{":
                            next_closing = Decoder._find_next_closing(t_gen, index, "{}")
                            new_gen_func = lambda: (j for i, j in enumerate(t_gen_func()) if index < i <= next_closing)

                            def dict_gen():
                                return (i for i in Decoder._init_dict_gen(new_gen_func))                        
                            yield dict_gen
                            index = next_closing

                        elif part == "(":
                            next_closing = Decoder._find_next_closing(t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(t_gen_func()) if index < i <= next_closing)
                            def tuple_gen(): 
                                return (i for i in Decoder._init_list_gen(new_gen_func, tuple_mode=1))
                            
                            yield tuple(Decoder._gen_normalize(tuple_gen))
                            index = next_closing
                            
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
                    yield Decoder._convert(part)
                    # luici kesinlikle kasıtlı değildi
                    lui=ci
                    # Yukarda demiştim zaten işte
                    # Kullanıldığını belirtme filan
                else:
                    # lui ile ci farklı olmazsa virgül koyulmadığını anlıyor
                    raise Exception("Syntax Error (,) (Code 004)")

    @staticmethod
    def _init_dict_gen(t_gen_func):
        t_gen = t_gen_func()
        key_val = ()
        is_on_value = False

        index = -1
        for part in t_gen:
            index += 1
            # Eğer tokensa
            if part in "[{(\\,:\"')}]":
                # Hangi tür olduğuna göre fonksiyon çağır
                if part in "[{(":
                    if len(key_val) == 0 and not is_on_value:
                        if part == "(":
                            next_closing = Decoder._find_next_closing(t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(t_gen_func()) if index < i <= next_closing)
                            def tuple_gen():
                                return (i for i in Decoder._init_list_gen(new_gen_func, tuple_mode=1))
                            key_val = (tuple(Decoder._gen_normalize(tuple_gen)), )
                            index = next_closing
                            
                        else:
                            raise Exception("Syntax Error {} (Code 011)")

                    elif len(key_val) == 1 and is_on_value:
                    # elif (ci-1) == lui: # and not len(key_val) == 2
                        if part == "[":
                            # Generator recursion
                            next_closing = Decoder._find_next_closing(t_gen, index, "[]")
                            new_gen_func = lambda: (j for i, j in enumerate(t_gen_func()) if index < i <= next_closing)
                            def list_gen():
                                return (i for i in Decoder._init_list_gen(new_gen_func))
                            
                            yield (key_val := (key_val[0], list_gen))
                            index = next_closing
                            
                        elif part == "{":
                            next_closing = Decoder._find_next_closing(t_gen, index, "{}")
                            new_gen_func = lambda: (j for i, j in enumerate(t_gen_func()) if index < i <= next_closing)
                            def dict_gen():
                                return (i for i in Decoder._init_dict_gen(new_gen_func))
                            
                            yield (key_val := (key_val[0], dict_gen))
                            index = next_closing

                        elif part == "(":
                            next_closing = Decoder._find_next_closing(t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(t_gen_func()) if index < i <= next_closing)
                            def tuple_gen():
                                return (i for i in Decoder._init_list_gen(new_gen_func, tuple_mode=1))
                            
                            yield (key_val := (key_val[0], tuple(Decoder._gen_normalize(tuple_gen))))
                            index = next_closing
                            

                        else:
                            raise Exception("Unknown Error (Code 00-1)")
                        
                    # else:
                    #     # virgül koymadan yeni eleman eklenemiyor
                    #     raise Exception("Syntax Error (,) (Code 004)")
                    
                elif part == "}":
                    break
                                
                elif part == ",":
                    key_val = ()
                    is_on_value = False
                
                elif part == ":":
                    if is_on_value:
                        raise Exception("Syntax Error (::) (Code 010)")
                    is_on_value = True

                elif part in ")]":
                    # Yanlış kapatma 
                    raise Exception("Syntax Error {)]} (Code 005)")
                    
            # Aktif parça token değilse
            else:
                part = Decoder._convert(part)
                # Key belirleniyorsa
                if not is_on_value:
                    key_val = (part, )

                # Key girilmişse
                elif len(key_val) == 1:
                    yield (key_val := (key_val[0], part))

                else:
                    raise Exception("Syntax Error (::) (Code 010)")

    @staticmethod
    def _find_next_closing(gen, index, type="[]"):
        cot = 1
        if len(type) != 2:
            raise Exception("Benim hatam...")
        
        while cot != 0:
            j, index = next(gen), index+1
            if j == type[0]:
                cot += 1
            elif j == type[1]:
                cot -= 1
        
        return index

    @staticmethod
    def _convert(part):
        # Şimdilik JSON uyumlu olsun hadi
        json = True
        part = part.strip()
        if json:
            if part == "null":
                # None
                return None
            
            elif part in ["true", "false"]:
                # Boolean
                return True if part == "true" else False

        if part in ["None"]:
            # None
            return None
        elif part[0] in "\"'" and part[-1] in "\"'" and part[0] == part[-1]:
            # String
            return part[1:-1]
        elif part.isdigit():
            # Integer
            return int(part)
        elif part.replace('.', '', 1).isdigit() or part in ["Infinity", "-Infinity", "NaN"]:
            # Float
            return float(part)
        elif part in ["True", "False"]:
            # Boolean
            return True if part == "True" else False
        else:
            raise Exception(f"Syntax Error [{part}] is not defined.")

    @staticmethod
    def _load(generator_func, is_generator="all"):
        generator_func2 = lambda: (j for i, j in enumerate(generator_func()) if i != 0)
        generator = generator_func()
        first_element = next(generator)
        
        # İlk eleman işlememiz gereken bir şeyse
        # Ne olduğuna göre işleyicileri çağır
        if first_element == "[":
            if is_generator:
                return Decoder._init_list_gen(generator_func2)
            else:
                def list_gen():
                    return (i for i in Decoder._init_list_gen(generator_func2))
                return Decoder._gen_normalize(list_gen)
            
        elif first_element == "{":
            if is_generator:
                return Decoder._init_dict_gen(generator_func2)
            else:
                def dict_gen():
                    return (i for i in Decoder._init_dict_gen(generator_func2))
                return Decoder._gen_normalize(dict_gen)
            
        elif first_element == "(":
            return tuple(Decoder._gen_normalize((i for i in Decoder._init_list_gen(generator, tuple_mode=1))))
                
        else:
            #   eğer direkt olarak sadece 1 değer 
            # okunmaya çalışılırsa token olmamalı
            try:
                next(generator)
            except StopIteration:
                return Decoder._convert(first_element)
            else:
                raise Exception("Syntax Error (Code 007)")
            # gen_next = "".join([i for i in generator])
            # part = str(first_element) + "".join(gen_next)

    @staticmethod
    def loads(string, is_generator="all"):
        # Bunu da
        generator_func = lambda: Decoder._tokenize_gen(string)
        return Decoder._load(generator_func, is_generator)

    @staticmethod
    def _gen_to_list(gen):
        final = []
        for i in gen:
            if isinstance(i, types.GeneratorType):
                final.append(Decoder._gen_to_list(i))
            else:
                final.append(i)
        return final

    @staticmethod
    def _gen_to_dict(gen):
        final = {}
        for key, value in gen:
            if isinstance(value, types.GeneratorType):
                final[key] = Decoder._gen_to_dict(value)
            else:
                final[key] = value
        return final

    @staticmethod
    def _gen_normalize(gen_func):
        gen = gen_func()
        if gen_func.__name__ == "dict_gen":
            final = {}
            for key, value in gen:
                if callable(value):
                    final[key] = Decoder._gen_normalize(value)
                else:
                    final[key] = value

        elif gen_func.__name__ in ["list_gen", "tuple_gen"]:
            final = []
            for value in gen:
                if callable(value):
                    final.append(Decoder._gen_normalize(value))
                else:
                    final.append(value)
        
        return final

    @staticmethod
    def _print_gen(gen, main=True):
        if isinstance(gen, types.GeneratorType):
            print("[", end="")
            for i in gen:
                if isinstance(i, types.GeneratorType):
                    Decoder._print_gen(i, main=False)
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

    @staticmethod
    def _read_gen(path, encoding="utf-8"):
        #   Dosyanın sonuna gelmediğimiz 
        # sürece sonraki elemanı okuyup yolla
        char = True
        with open(path, encoding=encoding) as f:
            while char:
                yield (char := f.read(1))

    @staticmethod
    def _read(path, encoding="utf-8"):
        # Hepsini oku yolla
        with open(path, encoding=encoding) as f:
            return f.read()
        # neden var bilmiyorum

    @staticmethod
    def load(path, is_generator="all", encoding="utf-8"):
        # Bunu anlatmayacağım
        generator_func = lambda: Decoder._tokenize_gen(Decoder._read_gen(path, encoding=encoding))
        return Decoder._load(generator_func, is_generator)
        
def _timer(func):
    #   ilk baştaki mal tokenizing algoritmamda sorting 
    # metodunu değiştirmenin ne kadar etkileyecğini görmek içindi
    def wrapper():
        # Güzel özellik 
        start = time.time()
        func()
        print(time.time() - start)
    return wrapper
    
    
@_timer
def test():
    # tester = [ "{", 
    #                     "'gen'", ":", "{", "'b'", ":", "'bb'", "}", ",", 
    #                     "'gen2'", ":", "{", "(", ")", ":", "{", "}", "}",
    #                 "}" ]
    # print(repr(tester)[1:-1]) 
    # print(loads(tester, is_generator=0))
    pass
    

if __name__ == "__main__":
    test()