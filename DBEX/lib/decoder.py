from dbex.lib.encryption import decrypter as defaultDecrypter
import types
import time
import json

default_tokenizers = "[{(\\,:\"')}]"


class Decoder:
    decrypter_func = defaultDecrypter

    @staticmethod
    def __tokenize(string, tokenizers=default_tokenizers):
        """Verilen tokenizerları verilen string (ya da generator) 
        içinden alıp ayıklıyor (string değer kontrolü yok)

        Args:
            string (str): [string ya da stringi döndüren bir generator]
            tokenizers (str): tokenizerlar işte. Defaults to Decoder.default_tokenizers.

        Yields:
            str: her bir özel parça ve arasında kalanlar
        """
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
    def __tokenize_gen(reader_gen, tokenizers=default_tokenizers):
        """her ne kadar __tokenize fonksiyonunda tokenlara ayırmış olsak da 
        tırnak işaretlerinin lanetine yakalanmaktan kurtulmak için bu fonksiyonu kullanıyoruz

        Args:
            reader_gen (Decoder.read_gen(dosya_yolu)): parça parça okunan değerleri yollayan herhangi bir generator olabilir
            tokenizers (str): tokenizerlar işte. Defaults to Decoder.default_tokenizers.

        Raises:
            Exception: String dışında backslash kullanıldığında patlıyor

        Yields:
            str: her bir parça (ya token ya da element)
        """
        #   eğer tırnak işaret ile string değer
        # girilmeye başlanmışsa değerlerin kaydolacağı liste
        active_str = None
        # Hangi tırnak işaretiyle başladığımız
        is_string = False
        # Önceki elemanın \ olup olmadığı
        is_prv_bs = False

        for part in Decoder.__tokenize(reader_gen, tokenizers):
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
    def __init_list_gen(t_gen_func, tuple_mode=False):
        """[ görüldüğünde çağırılan fonksiyon

        Args:
            t_gen_func (function): generator döndüren fonksiyon
            tuple_mode (bool): tuple mı olacak list mi (kapanış belli olsun diye). Defaults to False.

        Raises:
            Exception: Syntax Errorleri

        Yields:
            Her tipten şey döndürüyor. Ama parantez açma tarzı bir şey çıkarsa generator döndüren fonksiyon döndürüyor 
        """
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
                    if (ci - 1) == lui:
                        if part == "[":
                            next_closing = Decoder.__find_next_closing(
                                t_gen, index, "[]")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def list_gen():
                                return (i for i in Decoder.__init_list_gen(
                                    new_gen_func))

                            yield list_gen
                            index = next_closing

                        elif part == "{":
                            next_closing = Decoder.__find_next_closing(
                                t_gen, index, "{}")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def dict_gen():
                                return (i for i in Decoder.__init_dict_gen(
                                    new_gen_func))

                            yield dict_gen
                            index = next_closing

                        elif part == "(":
                            next_closing = Decoder.__find_next_closing(
                                t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def tuple_gen():
                                return (i for i in Decoder.__init_list_gen(
                                    new_gen_func, tuple_mode=1))

                            yield tuple(Decoder.gen_normalizer(tuple_gen))
                            index = next_closing

                        else:
                            raise Exception("Unknown Error (Code 00-1)")

                        # last used index -> lui
                        # current index -> ci

                        #   İçinde bulunduğumuz listenin
                        # kullandığımız indexinin kullanılmış olduğunu belirtiyoruz
                        lui = ci
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
                if (ci - 1) == lui:
                    # ekle işte
                    yield Decoder.__convert(part)
                    # luici kesinlikle kasıtlı değildi
                    lui = ci
                    # Yukarda demiştim zaten işte
                    # Kullanıldığını belirtme filan
                else:
                    # lui ile ci farklı olmazsa virgül koyulmadığını anlıyor
                    raise Exception("Syntax Error (,) (Code 004)")

    @staticmethod
    def __init_dict_gen(t_gen_func):
        """[ görüldüğünde çağırılan fonksiyon

        Args:
            t_gen_func (function): generator döndüren fonksiyon

        Raises:
            Exception: Syntax Errorleri

        Yields:
            Her tipten şey döndürüyor. Ama parantez açma tarzı bir şey çıkarsa generator döndüren fonksiyon döndürüyor.
        """
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
                            next_closing = Decoder.__find_next_closing(
                                t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def tuple_gen():
                                return (i for i in Decoder.__init_list_gen(
                                    new_gen_func, tuple_mode=1))

                            key_val = (tuple(
                                Decoder.gen_normalizer(tuple_gen)), )
                            index = next_closing

                        else:
                            raise Exception("Syntax Error {} (Code 011)")

                    elif len(key_val) == 1 and is_on_value:
                        # elif (ci-1) == lui: # and not len(key_val) == 2
                        if part == "[":
                            # Generator recursion
                            next_closing = Decoder.__find_next_closing(
                                t_gen, index, "[]")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def list_gen():
                                return (i for i in Decoder.__init_list_gen(
                                    new_gen_func))

                            yield (key_val := (key_val[0], list_gen))
                            index = next_closing

                        elif part == "{":
                            next_closing = Decoder.__find_next_closing(
                                t_gen, index, "{}")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def dict_gen():
                                return (i for i in Decoder.__init_dict_gen(
                                    new_gen_func))

                            yield (key_val := (key_val[0], dict_gen))
                            index = next_closing

                        elif part == "(":
                            next_closing = Decoder.__find_next_closing(
                                t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def tuple_gen():
                                return (i for i in Decoder.__init_list_gen(
                                    new_gen_func, tuple_mode=1))

                            yield (key_val :=
                                   (key_val[0],
                                    tuple(Decoder.gen_normalizer(tuple_gen))))
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
                part = Decoder.__convert(part)
                # Key belirleniyorsa
                if not is_on_value:
                    key_val = (part, )

                # Key girilmişse
                elif len(key_val) == 1:
                    yield (key_val := (key_val[0], part))

                else:
                    raise Exception("Syntax Error (::) (Code 010)")

    @staticmethod
    def __find_next_closing(gen, index, type="[]"):
        """sonraki parantez kapatma şeyini buluyor

        Args:
            gen (generator): Valla ne yaptığını hiç hatırlamıyorum
            index (int): kUSURA bakma
            type (str: "()", "[]", "{}"): [description]. Defaults to "[]".
            
        Returns:
            [type]: [description]
        """
        cot = 1
        if len(type) != 2:
            raise Exception("Benim hatam...")

        while cot != 0:
            j, index = next(gen), index + 1
            if j == type[0]:
                cot += 1
            elif j == type[1]:
                cot -= 1

        return index

    @staticmethod
    def __convert(part):
        """Verilen parçayı gerçek formuna büründürür (Bu dosyadaki tüm fonksiyonların amacı bu zaten ama)

        Args:
            part (str): parça

        Raises:
            Exception: Undefined variable

        Returns:
            part ama gerçek formu
        """
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
        elif part.replace('.', '', 1).isdigit() or part in [
                "Infinity", "-Infinity", "NaN"
        ]:
            # Float
            return float(part)
        elif part in ["True", "False"]:
            # Boolean
            return True if part == "True" else False
        else:
            raise Exception(f"Syntax Error [{part}] is not defined.")

    @staticmethod
    def __load(generator_func, *args, is_generator="all", **kwargs):
        """Loadların Lordu

        Args:
            generator_func (function): generator (tokenize_gen) döndüren fonksiyon
            is_generator (str, optional): generator objesinin sonda birleştirip birleştirilmeyeceğini belirliyor. Defaults to "all".

        Raises:
            Exception: Bakmaya üşendim

        Returns:
            is_generator false ise objenin kendisi
            true ise generator döndüren fonksiyon
        """
        generator_func2 = lambda: (j for i, j in enumerate(generator_func())
                                   if i != 0)
        generator = generator_func()
        first_element = next(generator)

        # İlk eleman işlememiz gereken bir şeyse
        # Ne olduğuna göre işleyicileri çağır
        if first_element == "[":

            def list_gen():
                return (i for i in Decoder.__init_list_gen(generator_func2))

            if is_generator:
                return list_gen
            else:
                return Decoder.gen_normalizer(list_gen)

        elif first_element == "{":

            def dict_gen():
                return (i for i in Decoder.__init_dict_gen(generator_func2))

            if is_generator:
                return dict_gen(generator_func2)
            else:
                return Decoder.gen_normalizer(dict_gen)

        elif first_element == "(":
            return tuple(
                # yapf: disable
                Decoder.gen_normalizer(
                    (i
                     for i in Decoder.__init_list_gen(generator, tuple_mode=1))
                ))

        else:
            #   eğer direkt olarak sadece 1 değer
            # okunmaya çalışılırsa token olmamalı
            try:
                next(generator)
            except StopIteration:
                return Decoder.__convert(first_element)
            else:
                raise Exception("Syntax Error (Code 007)")
            # gen_next = "".join([i for i in generator])
            # part = str(first_element) + "".join(gen_next)

    @staticmethod
    def load(path, *args, encoding="utf-8", **kwargs):
        # Bunun açıklaması init dosyasında olucak
        generator_func = lambda: Decoder.__tokenize_gen(
            Decoder.read_gen(path, encoding=encoding))
        return Decoder.__load(generator_func,
                              *args,
                              is_generator=False,
                              **kwargs)

    @staticmethod
    def loads(string, *args, gen_lvl=None, **kwargs):
        # Bunun açıklaması init dosyasında olucak
        generator_func = lambda: Decoder.__tokenize_gen(string)
        return Decoder.__load(generator_func,
                              *args,
                              gen_lvl=gen_lvl,
                              is_generator=(1 if gen_lvl is not None else 0),
                              **kwargs)

    @staticmethod
    def loader(path, *args, encoding="utf-8", gen_lvl="all", **kwargs):
        # Bunun açıklaması init dosyasında olucak
        generator_func = lambda: Decoder.__tokenize_gen(
            Decoder.read_gen(path, encoding=encoding))
        return Decoder.__load(generator_func,
                              *args,
                              gen_lvl=gen_lvl,
                              is_generator=(1 if gen_lvl is not None else 0),
                              **kwargs)

    @staticmethod
    def gen_normalizer(gen_func):
        """__load fonksiyonun generator fonksiyonunu objeye dönüştüren fonksiyon

        Args:
            gen_func (function): Generator döndüren fonksiyon alıyor (is_generator=0 __load'un çıktısı gibi)

        Returns:
            objenin kendisi
        """
        gen = gen_func()
        if gen_func.__name__ == "dict_gen":
            final = {}
            for key, value in gen:
                if callable(value):
                    final[key] = Decoder.gen_normalizer(value)
                else:
                    final[key] = value

        elif gen_func.__name__ in ["list_gen", "tuple_gen"]:
            final = []
            for value in gen:
                if callable(value):
                    final.append(Decoder.gen_normalizer(value))
                else:
                    final.append(value)

        return final

    @staticmethod
    def read_gen(path, encoding="utf-8"):
        """Dosya okuyucu (tek tek)

        Args:
            path (str): okunacak dosya yolu
            encoding (str): elleme. Defaults to "utf-8".

        Yields:
            str: her bir karakter
        """
        #   Dosyanın sonuna gelmediğimiz
        # sürece sonraki elemanı okuyup yolla
        char = True
        with open(path, encoding=encoding) as f:
            while char:
                yield (char := f.read(1))

    @staticmethod
    def read_gen_(path, encoding="utf-8"):
        #       her seferinde dosyayı açıp kaptması dosya okuma ve
        #   yazma bakımından hoş olmasına rağmen hız açısından
        # yeteri kadar verimli olacağını düşünmüyorum

        index = -1
        char = True
        while char:
            with open(path, encoding=encoding) as file:
                file.seek((index := index + 1), 0)
                yield (char := file.read(1))

    @staticmethod
    def read(path, encoding="utf-8"):
        """Normal direkt okuma

        Args:
            path (dosya yolu): okunacak dosya yolu 
            encoding (str, optional): elleme. Defaults to "utf-8".

        Returns:
            okunan dosyanın içinde yazanlar
        """
        # Hepsini oku yolla
        with open(path, encoding=encoding) as f:
            return f.read()

    @staticmethod
    def read_gen_wrapper(path, header_tokenizer="#", header_ender="\n"):
        "###56"  # örnek header
        index = 0
        # yapf: disable
        gen_func = lambda: Decoder._Decoder__tokenize(Decoder.read_gen_(path), tokenizers=header_tokenizer+header_ender)

        for i in gen_func():
            print(i)

        generator = gen_func()

        for part in generator:
            # alt satıra indiğinde iş bitti
            # ya da eğer ilk 3 eleman header tokenizera eşit değilse bozukluk var demektir
            if index < 3 and part != header_tokenizer or part == "\n":
                generator = gen_func()
                break

            elif index == 3 and type((converted_part := Decoder._Decoder__convert(part))) == int:
                ord_sum = converted_part
                if next(generator) == "\n" and next(generator) == "\n":
                    for part_ in generator:
                        ### Algoritma
                        for char in part_:
                            ord_sum -= ord(char)
                            yield char

                    if ord_sum != 0:
                        raise ValueError(f"File is corrupted... {ord_sum}")

                break

            index -= -1

        # header yoksa baştan başla hepsini gönder
        for i in generator:
            yield i

    @staticmethod
    def __ord_sum_writer(path):
        # geçici örnek
        with open(path, "r") as file:
            read = file.read()
        ord_sum = sum([ord(char) for char in read])
        with open(path, "w") as file:
            file.write(f"###{ord_sum}\n{read}")



def _timer(func):
    #   ilk baştaki mal tokenizing algoritmamda sorting
    # metodunu değiştirmenin ne kadar etkileyecğini görmek içindi
    def wrapper(*args, **kwargs):
        # Güzel özellik
        start = time.time()
        func(*args, **kwargs)
        print(time.time() - start)

    return wrapper
