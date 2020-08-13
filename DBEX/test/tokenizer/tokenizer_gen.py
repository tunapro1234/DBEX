import time

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


def tokenize_(string, tokenizers, settings=None, banned_chars=None):
    last_index = 0
    for index, char in enumerate(string):
        # ayıklanması istenen karakterlerden birine denk gelindiğinde
        if char in tokenizers:
            # last_index değişkeni ile ayıklancak karakter arasını ekle
            if index > (last_index + 1):
                yield "".join(string[(last_index + 1):index])
            # ayıklanacak karakteri ekle
            yield char
            # last_index değişkenini yenile
            last_index = index

        # Son elemandaysak ve eklenen son şey
        # bize verilen stringin son elemanı değilse
        elif index == len(string) - 1: # and last_index == index:
            # en son bulunan tokendan sonrasını da ekle
            yield "".join(string[(last_index + 1):])
        
        # ilk başta çıkarılması istenen karakterlerden biri varsa final arrayinin 
        # ilk elemanı "" oluyordu onu engellemek için alttaki list comprehension var
    # final = [j for i, j in enumerate(final) if j != ""] # and i != 0 
    
    # istenmeyen karakter belirtildiyse
    # if banned_chars is not None:
    #     banned_final = []
    #     # arrayin içindeki her parçanın her karakteri için
    #     for part in final:
    #         # istenmeyen karakter olup olmadığını kontrol edip istenenleri yeni değişkene ekle
    #         banned_final.append("".join([char for char in part if not char in banned_chars]))
    #     final = banned_final
        
    # return final


def tag_gen(arr):
    active_str = None
    is_string = False
    is_prv_bs = False
    for part in arr:
        # okuması daha kolay olsun diye
        if part in ["'", '"', "\\"]: 
            # parçanın tırnak olup olmadığını kontrol et
            if part in ["'", '"']:
                
                #   eğer string içinde değilsek 
                # is_string değişkenini tırnak işretine çevir
                
                # Bura zaten string içindeysek
                if is_string:
                    #   eğer string içindeysek ve
                    # tırnak işareti stringi açan tırnak işaretiyle 
                    # aktif tırnak işarti aynıysa stringi kapat
                    is_string = False if is_string == part else is_string
                    # aynı zamanda active_str değişkenini yok et dönüştür
                    
                    # eğer string hemen üst satırda kapatıldıysa (farklı tırnaksa kapanmıyor)
                    if not is_string:
                        # aktif string listesini string hale getirip döndür
                        active_str.append(part)
                        yield "".join(active_str)
                        # Sonra sıfırla                    
                        active_str = None
                        is_string = False
                        
                    # eğer gelen işaret açan işaretle aynı değilse
                    else:
                        active_str.append(part)
                
                # Bura string olayı yeni kurulduysa
                else:
                    is_string = part
                    active_str = [part]
                
                
            elif part == "\\":
                # önümüze \ geldiyse ve string içindeysek
                if is_string:
                    #   önceki parça backslash değilse önceki parçanın 
                    # backslash olduğuna dair uyarı yapmak için is_prv_bse True ver
                    if (is_prv_bs := bool(1 - is_prv_bs)):
                        active_str.append("\\")
                    # Eğer önceki parça backslashse salla gitsin
                        
                else:
                    raise Exception("Syntax Error (\\)")
                    # String içinde değilken backslash gelirse hata patlat
                
        else:
            if is_string:
                active_str.append(part)
            else:
                yield part

            # else:
            #     part = part.strip()
            #     if part.isdigit():
            #         tag = "int#"
            #     elif part.replace('.', '', 1).isdigit():
            #         tag = "float#"
            #     elif part in ["None"]:
            #         tag = "none#"
            #     elif part in ["True", "False"]:
            #         tag = "bool#"
            #     elif part == "":
            #         tag = "ignore#"
            #     else:
            #         print("Syntax Error (Code 001)")
            #         return False


def test():
    tokenizers = "[{(\\,\"')}]"
    # tester = ["[", "'", "tuna", "(", "pro", "'", "]"]
    tester = ["[", "'", '"', "tuna", "(", "pro", "'", "]"]
    for i in tokenize_gen(tester):
        print(i, end="")
        time.sleep(0.5)
    print("")


if __name__ == "__main__":
    test()