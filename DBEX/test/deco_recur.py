import time
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        rv = func(*args, **kwargs)
        print(time.time() - start)
        return rv
    return wrapper

@timer
def a(msg, lvl=0):
    if lvl > 2:
        return "".join([i for i in a(msg, lvl+1)])
    else:
        

def test():
    a("hello")
    

if __name__ == "__main__":
    test()
