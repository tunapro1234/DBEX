def dump_gen_(obj, max_gen_lvl=1, gen_lvl=1, indent="", seperators=(", ", ": ")):
    if type(seperators) != tuple:
        raise Exception("Seperator error")
    
    parser1 = seperators[1]
    parser2 = seperators[0].rstrip() if indent else seperators[0]
    
    if type(obj) in [list, tuple]:
        first = True
        yield "(" if type(obj) == tuple else "["
        
        for element in obj:
            if not first:
                yield parser2 + "\n" + indent*(gen_lvl+1) if indent else parser2
            
            elif indent:
                yield "\n" + indent*(gen_lvl+1)
            
            for i in dump_gen(element, max_gen_lvl, gen_lvl+1, indent):
                yield i
            
            first = False

        if indent:
            yield "\n" + indent*gen_lvl
        yield ")" if type(obj) == tuple else "]"
    
    elif type(obj) == dict:
        yield "{"
        first = True
        
        for key, value in obj.items():
            if not first:
                yield parser2 + "\n" + indent*(gen_lvl+1) if indent else parser2
            
            elif indent:
                yield "\n" + indent*(gen_lvl+1)
            
            # key döndürme
            yield "".join([i for i in dump_gen_(key, max_gen_lvl, gen_lvl, "")]) if type(key) == tuple else convert_(key)
            yield parser1
            
            # value döndürme            
            for i in dump_gen(value, max_gen_lvl, gen_lvl+1, indent):
                yield i
            
            first = False
        
        if indent:
            yield "\n" + indent*gen_lvl
        yield "}"
    
    else:
        yield obj

def dump_gen(element, max_gen_lvl=0, gen_lvl=0, indent=0, seperators=(", ", ": ")):
    indent = " " * indent if type(indent) == int else indent
    
    if type(element) in [tuple, list, dict]:
        if gen_lvl < max_gen_lvl:
            for i in dump_gen_(element, max_gen_lvl, gen_lvl, indent, seperators):
                yield i
        else:
            yield "".join([i for i in dump_gen_(element, max_gen_lvl, gen_lvl, indent, seperators)])
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
    
    
def dumps(obj, max_gen_lvl=0, gen_lvl=0, indent=0, seperators=(", ", ": "), sort_keys=0): 
    if sort_keys:
        return sort_keys("".join([i for i in dump_gen(obj, max_gen_lvl=0, gen_lvl=0, indent=0, seperators=(", ", ": "))]))
    else:
        return "".join([i for i in dump_gen(obj, max_gen_lvl=0, gen_lvl=0, indent=0, seperators=(", ", ": "))])

def dump():
    pass

if __name__ == "__main__":
    import json
    tester = ["tunapro", [[]], [[]], [[0, "[\\]"]]]
    dumps(tester)
    correct_result = '["tunapro", [[]], [[]], [[0, "[\\]"]]]'
