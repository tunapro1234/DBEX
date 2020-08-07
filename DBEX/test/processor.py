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
                elif part == " ":
                    tag = "ignore#"
                else:
                    print("Tokenizing error.")
                    return False
        if tag != "ignore#":
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
    
    
    if not_final[0].data == "[":
        return init_list(not_final[1:])
    elif not_final[0].data == "{":
        return init_dict(not_final[1:])
    elif not_final[0].data == "(":
        return init_tuple(not_final[1:])
    

def init_list(t_list):    
    i = 0
    final = []
    last_used_index = -1
    current_index = 0
    while i < len(t_list):
        part = t_list[i]
        
        if "token" in part.tags:
            if part.data == "[":            
                next_closing = [j for j in range(len(t_list)) if t_list[j].data == "]" and j > i]
                
                if len(next_closing) == 0:
                    print("Tokenizing Error 3.")
                    return False 
                
                next_closing = next_closing[0]
                if (current_index-1) == last_used_index:
                    final.append(init_list(t_list[(i+1):(next_closing+1)]))
                    last_used_index = current_index
                else:
                    print("Tokenizing Error 4,")
                    return False
                i = next_closing
            
            elif part.data == "(":
                next_closing = [j for j in range(len(t_list)) if t_list[j].data == ")"]
                if len(next_closing) == 0:
                    print("Tokenizing Error 3.")
                    return False
                
                next_closing = next_closing[0]
                if (current_index-1) == last_used_index:
                    final.append(init_tuple(t_list[(i+1):(next_closing+1)]))
                    last_used_index = current_index
                else:
                    print("Tokenizing Error 4,")
                    return False
                i = next_closing
            
            elif part.data == "{":
                next_closing = [j for j in range(len(t_list)) if t_list[j].data == "}"]
                if len(next_closing) == 0:
                    print("Tokenizing Error 3.")
                    return False
                
                next_closing = next_closing[0]
                if (current_index-1) == last_used_index:
                    final.append(init_dict(t_list[(i+1):(next_closing+1)]))
                    last_used_index = current_index
                else:
                    print("Tokenizing Error 4,")
                    return False
                i = next_closing
                
            elif part.data == "]":
                return final
            
            elif part.data == ",":
                current_index += 1
        
        else:
            if (current_index-1) == last_used_index:
                final.append(part.data)    
                last_used_index = current_index
            else:
                print("Tokenizing Error 4,")
                return False
        
        i += 1
    
    return final
    
def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(time.time() - start)
    return wrapper
    
@timer
def test():
    print(process_("[['tuna(pro)'], 1234, []]"))

if __name__ == "__main__":
    test()