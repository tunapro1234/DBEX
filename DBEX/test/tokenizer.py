# from DBEX.lib.sortingAlgorithm import sort_list
import time

def sort_list(list1):
    for j in range(len(list1)-1, 0, -1):
        for i in range(len(list1)):
            if (i + 1) != len(list1) and list1[i] > list1[i + 1]:
                list1[i], list1[i + 1] = list1[i + 1], list1[i]
    return list1   

def tokenize_(string, tokenizers, settings=None, banned_chars = None):
    ### girdilerin doğruluğu kontrol ediliyor
    try:
        if type(tokenizers[0]) != str or type(string[0]) != str: 
            raise Exception("")
    except:
        print("Tokenizer input error")
        return False
      
    indexes = []
    for token in tokenizers:
        tokenizer_index = [i for i in range(len(string)) if string[i] == token]
        if len(tokenizer_index) > 0:
            for i in tokenizer_index:
                indexes.append(i)
    
    indexes = sort_list(indexes)
    final_string = []
    if indexes[0] != 0:
        final_string = [string[:indexes[0]]]
    
    for i in range(len(indexes)):
        final_string.append(string[indexes[i]])
        if i != len(indexes) - 1 and indexes[i+1] - indexes[i] > 1:
            final_string.append(string[(indexes[i]+1):(indexes[i+1])])
    
    if banned_chars is not None:
        for char in banned_chars:
            final_string = [i for i in final_string if i != char]
    
    return final_string

@timer
def test():
    print(tokenize_("(tunapro1234)", "(1)"))

if __name__ == "__main__":
    test()