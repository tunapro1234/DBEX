"""TODO
indent
sort_items
"""


def dump_gen_(obj, max_gen_lvl=1, gen_lvl=1, indent=0):
    parser1 = ":"
    parser2 = ", "
    if type(obj) in [list, tuple]:
        first = True
        yield "(" if type(obj) == tuple else "["
        
        for element in obj:
            if not first:
                yield parser2
            
            for i in dump_gen(element, max_gen_lvl, gen_lvl+1):
                yield i
            
            first = False
        
        yield ")" if type(obj) == tuple else "]"
    
    elif type(obj) == dict:
        yield "{"
        first = True
        
        for key, value in obj.items():
            if not first:
                yield parser2
             
            # key döndürme
            yield "".join([i for i in dump_gen_(key, max_gen_lvl, gen_lvl)]) if type(key) == tuple else convert_(key)
            yield parser1
            
            # value döndürme            
            for i in dump_gen(value, max_gen_lvl, gen_lvl+1):
                yield i
            
            first = False
        
        yield "}"
    
    else:
        yield obj

def dump_gen(element, max_gen_lvl, gen_lvl=0):
    if type(element) in [tuple, list, dict]:
        if gen_lvl < max_gen_lvl:
            for i in dump_gen_(element, max_gen_lvl, gen_lvl):
                yield i
        else:
            yield "".join([i for i in dump_gen_(element, max_gen_lvl, gen_lvl)])
    else:
        yield convert_(element)
        
    
def convert_(element):
    if element in [float("Infinity"), float("-Infinity")] or element != element:
        if element == float("Infinity"):
            return "Infinity"
        elif element == float("-Infinity"):
            return "-Infinity"
        elif element != element:
            return "NaN"
    else:
        return f'"{element}"' if type(element) == str else str(element)
    
    
def dumps(obj):
    pass


def dump():
    pass

def test():
    obj = {
        "a":"aa",
        "b":[
            {"name": "tuna"},
            {"name": "uras"},
            [
                {"lastname": "gül"},
                {"lastname": "gül"},
                {"lastname": "hep"}
            ]
        ]
    }
    for i in dump_gen(obj, 5):
        print(i, end="")
    

if __name__ == "__main__":
    test()