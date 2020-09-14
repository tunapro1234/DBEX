from dbex.lib.encryption import decrypter
import dbex.res.globalv as gvars
import types, time


def version():
    with open("dbex/res/VERSION.txt") as file:
        return file.read()


__version__ = version()


class DBEXDecodeError(ValueError):
    # biraz çaldım gibi
    def __init__(self, msg, code, pos="Unknown"):

        code = (3 - len(str(code))) * '0' + str(code)
        errmsg = f"{msg} (Code: {code}): (char {pos})"
        ValueError.__init__(self, errmsg)

        self.code = code
        self.msg = msg
        self.pos = pos

    def __reduce__(self):
        return self.__class__, (self.msg, self.doc, self.pos)


class Decoder:
    default_tokenizers = "[{(\\,:\"')}]"
    header_shape = gvars.header_shape

    def __init__(self,
                 header=True,
                 encryption=None,
                 default_path=None,
                 default_max_depth=0,
                 database_shape=None,
                 default_sort_keys=0,
                 encryption_pass=None,
                 default_header_path=None,
                 changed_file_action=0,
                 default_file_encoding="utf-8"):
        self.default_file_encoding = default_file_encoding
        self.changed_file_action = changed_file_action
        self.default_header_path = default_header_path
        self.default_sort_keys = default_sort_keys
        self.encryption_pass = encryption_pass
        self.default_max_depth = default_max_depth
        self.database_shape = database_shape
        self.default_path = default_path
        self.encryption = encryption
        self.header = header

    def __tokenize(self, string, tokenizers=None):
        """Verilen tokenizerları verilen string (ya da generator) 
        içinden alıp ayıklıyor (string değer kontrolü yok)

        Args:
            string (str): [string ya da stringi döndüren bir generator]
            tokenizers (str): tokenizerlar işte. Defaults to Decoder.default_tokenizers.

        Yields:
            str: her bir özel parça ve arasında kalanlar
        """
        tokenizers = self.default_tokenizers if tokenizers is None else tokenizers
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

    def __tokenize_gen(self, reader_gen, tokenizers=None):
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
        errpos = 0
        tokenizers = self.default_tokenizers if tokenizers is None else tokenizers
        #   eğer tırnak işaret ile string değer
        # girilmeye başlanmışsa değerlerin kaydolacağı liste
        active_str = None
        # Hangi tırnak işaretiyle başladığımız
        is_string = False
        # Önceki elemanın \ olup olmadığı
        is_prv_bs = False

        for part in self.__tokenize(reader_gen, tokenizers):
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
                        raise DBEXDecodeError(
                            "String dışında backslah kullanılamaz.",
                            code=10,
                            pos=errpos)
                        # Karakter karakter okuduğum için satır sonlarında (\n) umarım sıkıntı çıkarmaz

            else:
                # Stringse ekle değilse yolla
                if is_string:
                    active_str.append(part)

                elif part.strip() != "":
                    yield part

            errpos += len(part)

    def __init_list_gen(self,
                        t_gen_func,
                        tuple_mode=False,
                        max_depth=None,
                        gen_lvl=1):
        """[ görüldüğünde çağırılan fonksiyon

        Args:
            t_gen_func (function): generator döndüren fonksiyon
            tuple_mode (bool): tuple mı olacak list mi (kapanış belli olsun diye). Defaults to False.

        Raises:
            Exception: Syntax Errorleri

        Yields:
            Her tipten şey döndürüyor. Ama parantez açma tarzı bir şey çıkarsa generator döndüren fonksiyon döndürüyor 
        """
        # gereksiz ama koymakta fayda var
        max_depth = self.default_max_depth if max_depth is None else max_depth

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
                            next_closing = self.__find_next_closing(
                                t_gen, index, "[]")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def list_gen():
                                return (i for i in self.__init_list_gen(
                                    new_gen_func,
                                    max_depth=max_depth,
                                    gen_lvl=gen_lvl + 1))

                            if max_depth == "all" or gen_lvl < max_depth:
                                yield list_gen
                            else:
                                yield self.gen_normalizer(list_gen)

                            index = next_closing

                        elif part == "{":
                            next_closing = self.__find_next_closing(
                                t_gen, index, "{}")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def dict_gen():
                                return (i for i in self.__init_dict_gen(
                                    new_gen_func,
                                    max_depth=max_depth,
                                    gen_lvl=gen_lvl + 1))

                            if max_depth == "all" or gen_lvl < max_depth:
                                yield dict_gen
                            else:
                                yield self.gen_normalizer(dict_gen)

                            index = next_closing

                        elif part == "(":
                            next_closing = self.__find_next_closing(
                                t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def tuple_gen():
                                return (i for i in self.__init_list_gen(
                                    new_gen_func, tuple_mode=1, max_depth=0))

                            yield tuple(self.gen_normalizer(tuple_gen))
                            index = next_closing

                        else:
                            raise DBEXDecodeError(
                                "Teknik olarak bu yazıyı okuyor olman mümkün değil",
                                code=-3)

                        # last used index -> lui
                        # current index -> ci

                        #   İçinde bulunduğumuz listenin
                        # kullandığımız indexinin kullanılmış olduğunu belirtiyoruz
                        lui = ci
                        #   ki virgül koymadan yeni bir indexe atlamasın
                        # işte virgül koyunca ci yi bir arttırıyoruz sonra ikisi farklı oluyor filan

                    else:
                        # virgül koymadan yeni eleman eklenemiyor
                        raise DBEXDecodeError(
                            "Virgül koymadan yeni eleman eklenemez", code=20)

                elif part == closing:
                    # kapatıyorsan kapat
                    break

                elif part == ",":
                    # Current indexi arttır ki
                    ci += 1
                    # son kullanılmış olanla aynı olmasın

                elif part in err_closing:
                    # Yanlış kapatma
                    raise DBEXDecodeError("Yanlış parantez kapatma ( ]} )",
                                          code=21)
                    # Zaten kesin daha önce syntax error döndürür

            # Aktif parça token değilse
            else:
                # Virgül koyulup yeni yer açılmışsa
                if (ci - 1) == lui:
                    # ekle işte
                    yield self.__convert(part)
                    # luici kesinlikle kasıtlı değildi
                    lui = ci
                    # Yukarda demiştim zaten işte
                    # Kullanıldığını belirtme filan
                else:
                    # lui ile ci farklı olmazsa virgül koyulmadığını anlıyor
                    raise DBEXDecodeError(
                        "Virgül koymadan yeni eleman eklenemez", code=22)

    def __init_dict_gen(self, t_gen_func, max_depth=None, gen_lvl=1):
        """[ görüldüğünde çağırılan fonksiyon

        Args:
            t_gen_func (function): generator döndüren fonksiyon

        Raises:
            Exception: Syntax Errorleri

        Yields:
            Her tipten şey döndürüyor. Ama parantez açma tarzı bir şey çıkarsa generator döndüren fonksiyon döndürüyor.
        """
        # gereksiz ama koymakta fayda var
        max_depth = self.default_max_depth if max_depth is None else max_depth

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
                            next_closing = self.__find_next_closing(
                                t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def tuple_gen():
                                return (i for i in self.__init_list_gen(
                                    new_gen_func, tuple_mode=1))

                            key_val = (tuple(self.gen_normalizer(tuple_gen)), )
                            index = next_closing

                        else:
                            raise DBEXDecodeError("Dictionary key değerinde mutable obje türü kullanılamaz", code=30)

                    elif len(key_val) == 1 and is_on_value:
                        # elif (ci-1) == lui: # and not len(key_val) == 2
                        if part == "[":
                            # Generator recursion
                            next_closing = self.__find_next_closing(
                                t_gen, index, "[]")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def list_gen():
                                return (i for i in self.__init_list_gen(
                                    new_gen_func,
                                    max_depth=max_depth,
                                    gen_lvl=gen_lvl + 1))

                            if max_depth == "all" or gen_lvl < max_depth:
                                yield (key_val := (key_val[0], list_gen))
                            else:
                                yield (key_val :=
                                       (key_val[0],
                                        self.gen_normalizer(list_gen)))

                            index = next_closing

                        elif part == "{":
                            next_closing = self.__find_next_closing(
                                t_gen, index, "{}")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def dict_gen():
                                return (i for i in self.__init_dict_gen(
                                    new_gen_func,
                                    max_depth=max_depth,
                                    gen_lvl=gen_lvl + 1))

                            if max_depth == "all" or gen_lvl < max_depth:
                                yield (key_val := (key_val[0], dict_gen))
                            else:
                                yield (key_val :=
                                       (key_val[0],
                                        self.gen_normalizer(dict_gen)))

                            index = next_closing

                        elif part == "(":
                            next_closing = self.__find_next_closing(
                                t_gen, index, "()")
                            new_gen_func = lambda: (j for i, j in enumerate(
                                t_gen_func()) if index < i <= next_closing)

                            def tuple_gen():
                                return (i for i in self.__init_list_gen(
                                    new_gen_func, tuple_mode=1, max_depth=0))

                            yield (key_val :=
                                   (key_val[0],
                                    tuple(self.gen_normalizer(tuple_gen))))
                            index = next_closing

                        else:
                            raise DBEXDecodeError("Bu hatayı aldığına göre library artık kullanılmıyordur", code=-3)

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
                        raise DBEXDecodeError("Çok fazla iki nokta (:)", code=32)
                    is_on_value = True

                elif part in ")]":
                    # Yanlış kapatma
                    raise DBEXDecodeError("Yanlış parantez kapatma ( )] )", code=33)

            # Aktif parça token değilse
            else:
                part = self.__convert(part)
                # Key belirleniyorsa
                if not is_on_value:
                    key_val = (part, )

                # Key girilmişse
                elif len(key_val) == 1:
                    yield (key_val := (key_val[0], part))

                else:
                    raise DBEXDecodeError("Çok fazla iki nokta (:)", code=34)

    def __find_next_closing(self, gen, index, type="[]"):
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

    def __convert(self, part):
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
            raise DBEXDecodeError(f"Tanımlanmamış obje ya da keyword : [{part}]", code=40)

    def __load(self, generator_func, max_depth=None, **kwargs):
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

        max_depth = self.default_max_depth if max_depth is None else max_depth

        # yapf: disable
        generator_func2 = lambda: (j for i, j in enumerate(generator_func()) if i != 0)
        generator = generator_func()
        first_element = next(generator)

        # İlk eleman işlememiz gereken bir şeyse
        # Ne olduğuna göre işleyicileri çağır
        if first_element == "[":

            def list_gen():
                return (i for i in self.__init_list_gen(generator_func2, max_depth=max_depth))

            if max_depth == "all" or max_depth > 0:
                return list_gen
            else:
                return self.gen_normalizer(list_gen)

        elif first_element == "{":

            def dict_gen():
                return (i for i in self.__init_dict_gen(generator_func2, max_depth=max_depth))

            if max_depth == "all" or max_depth > 0:
                return self.gen_normalizer(dict_gen)
            else:
                return dict_gen(generator_func2)

        elif first_element == "(":

            def tuple_gen():
                return (i for i in self.__init_list_gen(generator, tuple_mode=1, max_depth=0))

            return tuple(self.gen_normalizer(tuple_gen))

        else:
            #   eğer direkt olarak sadece 1 değer
            # okunmaya çalışılırsa token olmamalı
            try:
                next(generator)
            except StopIteration:
                return self.__convert(first_element)
            else:
                raise DBEXDecodeError("Verilen dosya ya da string içinde 1'den fazla obje olamaz", code=50)
            # gen_next = "".join([i for i in generator])
            # part = str(first_element) + "".join(gen_next)

    def load(self, path=None, encoding=None, **kwargs):
        """json.load'un çakması

        Args:
            path (str): dosya yolu
            encoding (str): Defaults to "utf-8".

        Returns:
            Dosyada yazılı olan obje
        """
        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        generator_func = lambda: self.__tokenize_gen(
            self.read_gen(path, encoding=encoding))
        return self.__load(generator_func, is_generator=False, **kwargs)

    def loads(self, string, max_depth=None, **kwargs):
        """json.loads'un çakması ve generator olabiliyor

        Args:
            string (str): dönüştürülmesi istenen obje
            is_generator (int, optional): Generator olup olmayacağı. Defaults to 0.

        Returns:
            Eğer is_generator True verilirse generator döndüren fonksiyon döndürüyor,
            değilse direkt olarak objenin kendisini döndürüyor
        """
        # max depth kontrolü __loadda yapılıyor
        generator_func = lambda: self.__tokenize_gen(string)
        return self.__load(generator_func,
                           max_depth=max_depth,
                           **kwargs)

    def loader(self, path=None, encoding=None, max_depth="all", **kwargs):
        """json.load'un generator hali

        Args:
            path (str): okunacak dosyanın yolu
            cls (class): Decoder classı (elleme). Defaults to Decoder from dbex.lib.decoder.
            decrypter (function): decryption türü. Defaults to empty_decrypter from dbex.lib.encryption.
            
            encoding (str): Defaults to "utf-8".
            gen_lvl (int, str): generator objesinin derinliği. Defaults to "all".

        Returns:
            (Dosyada yazanları döndüren generator) objesi döndüren bir fonksiyon
        """
        max_depth = self.default_max_depth if max_depth is None else max_depth

        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        generator_func = lambda: self.__tokenize_gen(
            self.read_gen(path, encoding=encoding))
        return self.__load(generator_func,
                           max_depth=max_depth,
                           **kwargs)

    def gen_normalizer(self, gen_func):
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
                    final[key] = self.gen_normalizer(value)
                else:
                    final[key] = value

        elif gen_func.__name__ in ["list_gen", "tuple_gen"]:
            final = []
            for value in gen:
                if callable(value):
                    final.append(self.gen_normalizer(value))
                else:
                    final.append(value)

        return final

    def read_gen(self, path=None, encoding=None):
        """Dosya okuyucu (tek tek)

        Args:
            path (str): okunacak dosya yolu. None verilirse defaultu alır
            encoding (str): elleme. None verilirse defaultu alır

        Yields:
            str: her bir karakter
        """
        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        #   Dosyanın sonuna gelmediğimiz
        # sürece sonraki elemanı okuyup yolla
        char = True
        with open(path, encoding=encoding) as f:
            while char:
                yield (char := f.read(1))

    def read_gen_safe(self, path=None, encoding=None):
        #       her seferinde dosyayı açıp kaptması dosya okuma ve
        #   yazma bakımından hoş olmasına rağmen hız açısından
        # yeteri kadar verimli olacağını düşünmüyorum

        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        index = -1
        char = True
        while char:
            with open(path, encoding=encoding) as file:
                file.seek((index := index + 1), 0)
                yield (char := file.read(1))

    def read(self, path=None, encoding=None):
        """Normal direkt okuma

        Args:
            path (dosya yolu): okunacak dosya yolu 
            encoding (str, optional): elleme. Defaults to "utf-8".

        Returns:
            okunan dosyanın içinde yazanlar
        """
        path = self.default_path if path is None else path
        encoding = self.default_file_encoding if encoding is None else encoding

        # Hepsini oku yolla
        with open(path, encoding=encoding) as f:
            return f.read()

    def __find_header_path(self, path=None):
        # biraz sakat
        path = self.default_path if path is None else path
        seperator = "\\" if "\\" in path else "/"
        spath = path.split(seperator)
        new_path = seperator.join([i for i in spath + [f".{spath[-1]}.chex"]])
        return new_path

    def header_reader(self,
                      path=None,
                      header_tokenizer="#",
                      header_ender="\n",
                      safe=True):

        path = self.default_path if path is None else path
        self.deafult_header_path = path = self.__find_header_path(
            self.default_path) if path is None else path

        gen_func = self.loader(path, gen_lvl=1)
        gen = gen_func()

        for key, value in gen:
            if key == "database_shape" and value:
                pass

            elif key == "hash":
                pass

            elif key == "version":
                pass

            elif key == "header_hash":
                pass

            else:
                self.preform_action(path, self.header_shape)

    def preform_action(self, path):
        if self.changed_file_action == 1:
            print(f"[WARN] The file has changed: [{path}]")

        elif self.changed_file_action > 2:
            self.reset_file(path)

        elif self.changed_file_action > 3:
            with open(path, "w+") as file:
                file.write("")

    def reset_file(self, path, shape):
        pass
