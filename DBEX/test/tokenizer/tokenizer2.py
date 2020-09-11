# Dün yazdığım fonsiyonun gereksizliğini fark ettim.
# Sorting olayını işin içinden çıkarmanın programın performansına yansımasını umuyorum.

import time


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
        elif index == len(string) - 1:  # and last_index == index:
            # en son bulunan tokendan sonrasını da ekle
            final.append(string[(last_index + 1):])

        # ilk başta çıkarılması istenen karakterlerden biri varsa final arrayinin
        # ilk elemanı "" oluyordu onu engellemek için alttaki list comprehension var
    final = [j for i, j in enumerate(final) if j != ""]  # and i != 0

    # istenmeyen karakter belirtildiyse
    if banned_chars is not None:
        banned_final = []
        # arrayin içindeki her parçanın her karakteri için
        for part in final:
            # istenmeyen karakter olup olmadığını kontrol edip istenenleri yeni değişkene ekle
            banned_final.append("".join(
                [char for char in part if not char in banned_chars]))
        final = banned_final

    return final


def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(time.time() - start)

    return wrapper


@timer
def test():
    print(tokenize_("(tunapro1234)", "(1)"))


if __name__ == "__main__":
    test()