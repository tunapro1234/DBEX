import types
def find_next_closing(arr, index, type="[]"):
    cot = 1
    for i in range(index, len(arr)):        
        if arr[i] == type[0]:
            cot += 1
        elif arr[i] == type[1]:
            cot -= 1
        
        if cot == 0:
            return i
        
def b(arr):
    skip = 0
    next_closing = 0
    for index, part in enumerate(arr):
        if skip:
            if skip == index:
                next_closing, skip = False, False
            else:
                continue
        if part == "[":
            next_closing = find_next_closing(arr, index, "[]")
            yield (i for i in b(arr[(index+1):next_closing]))
            skip = (next_closing+1)
        
        elif part == "]":
            break
            
        else:
            yield part
    
def init_list(gen):
    final = []
    for i in gen():
        if callable(i):
            final.append(init_list(i))
        else:
            final.append(i)
    return final
    
def gen_to_list(gen):
    final = []
    for i in gen:
        if isinstance(i, types.GeneratorType):
            final.append(gen_to_list(i))
        else:
            final.append(i)
    return final
    
def a():
    return b    

def empty(*args, **kwargs):
    return args, kwargs

if __name__ == "__main__":
    test_arr = ["[", "[", "'tunapro'", "]", "]"]
    
    if test_arr[0] == "[":
        print(gen_to_list((i for i in b(test_arr[1:]))))
    