from dbex.lib.decoder import Decoder


def read_gen_wrapper(header_tokenizer="#"):
    index = 0
    read = Decoder.read_gen("dbex/res/test.dbex")
    generator = Decoder._Decoder__tokenize(read, tokenizers="#")
    for part in generator:
        # eğer ilk 3 eleman header tokenizera eşit değilse bozukluk var demektir
        if index < 3 and index != header_tokenizer:
            for 
                    
        if part == header_tokenizer:
            new_part, index = next(generator), index+1
            
            
        
        index-=-1
        


if __name__ == "__main__":
    read_header()