import time

def tokenize_(string, tokenizers, settings=None, banned_chars = None):
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
    

# tokenizers = "([\"\'\'\"])"
# final = tokenize_(string, tokenizers + ":=,")
# if len([i for i in string if i in tokenizers[:len(tokenizers)//2]]) != len([j for j in string if j in tokenizers[(len(tokenizers)//2)+1:]]):
#     print("Input error.")
#     return False 


def process_(string):
    class Part:
        def __init__(self, data, tags):
            self.data = data
            self.tags = tags

        def __str__(self):
                return "DATA: " + str(self.data) + " ### TAGS: " + str(self.tags)
    
    tokenizers = "({[\"''\"]})"
    
    #region Parçaları isimlendirme
    not_final = []
    is_string = False
    string = tokenize_(string, tokenizers + ":=,", banned_chars=" ")
    for part in string:
        if part in tokenizers + ":=,":
            if part == "'" or part == '"':
                is_string = bool(1 - is_string)
                tag = "token#"
            elif not is_string:
                tag = "token#"
            else:
                tag = "str#"
        else:
            if is_string:
                tag = "str#"
            else:
                if part.isdigit():
                    tag = "int#"
                else:
                    print("Tokenizing error.")
                    return False
        
        not_final.append(Part(part, tag))
    #endregion
    
    
    #region   Parantez ve tırnak gibi şeylerin açılma ve 
    # kapanma sayılarının aynı olup olmadığının kontrolü
    comp = [part.data for part in not_final if "token" in part.tags]
    
    a = [i for i in comp if i in tokenizers[:len(tokenizers)//2]]
    b = [j for j in comp if j in tokenizers[(len(tokenizers)//2):]]
    if len(a) != len(b):
        print("Input error.")
        return False 
    a, b = None, None
    
    # # DEBUG SKILLS
    # ############################################    
    # print("\n".join([str(i) for i in not_final]))
    # ############################################    
    # print("\n"*3)
    #endregion
    
    
    #region Aslında string olan tokenları temizleme
    prev_tag = ""
    new_not_final = []
    for part in not_final:
        if prev_tag == part.tags and not "token" in part.tags:
            new_not_final[-1].data += part.data
        else:
            new_not_final.append(part)
            prev_tag = part.tags
    not_final = new_not_final
    new_not_final = None

    #endregion #########################################    
    
    
    dicts = []
    arrays = []
    tuples = []
    # last_indexes = []
    
    new_tags = ""
    for index, part in enumerate(not_final):
        if "token" in part.tags:
            new_tags = "#".join(["el_of_ar" + str(i) for i, j in enumerate(arrays) if j[0] == True]) + "#"
            # new_tags = "#".join(["eofarr" + str(i) for i, j in enumerate(arrays) if j[0] == True]) + "#"
            # new_tags = "#".join(["eofarr" + str(i) for i, j in enumerate(arrays) if j[0] == True]) + "#"
            
            if part.data == "[":            
                part.tags += "st_of_ar" + str(len(arrays)) + "#"
                # last_indexes.append(0)
                arrays.append([True, str(len(arrays)), 0])
                
                # b = new_not_final
                # for i, j in enumerate(last_indexes):
                #     if i+1 != len(last_indexes):
                #         b = b[j]
                #     else:
                #         b.append([])
                        
                        
            elif part.data == "]":

                # En son açık olan array kapatıldı (en içerdeki)
                a = [i for i, j in enumerate(arrays) if j[0] == True]
                if len(a) == 0:
                    print("Tokenizing error 2.")
                    return False
                arrays[a[-1]][0] = False 

                # kapatılan arrayin indexleri silindi
                # last_indexes = [last_indexes[i] for i in range(len(last_indexes)) if i+1 != len(last_indexes)]
                part.tags += "end_of_ar" + str(a[-1]) + "#"
                new_tags = ""
        
            elif part.data == ",":
                c = [i for i in arrays if i[0] == True]
                if len(c) == 0:
                    print("Tokenizing error 3.")
                    return False
                arrays[c[-1]][2] += 1 
                # last_indexes[-1] += 1
        
        part.tags += new_tags
        not_final[index] = part
        new_tags = ""        
    
    print(arrays)
    return "\n".join([str(i) for i in not_final])    
    # return final
    
def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(time.time() - start)
    return wrapper
    
@timer
def test():
    print(process_("[['tuna(pro)'], 1234][]"))

if __name__ == "__main__":
    test()