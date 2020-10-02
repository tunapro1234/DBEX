def dict_sort(inputObj: dict):
    # yapf: disable
    return {k: v for k, v in sorted(inputObj.items(), key=lambda item: item[1])}
    # evet stackoverflow

def sorter(inputObj, *a, **kw):
    if type(inputObj) is list:
        for index, element in enumerate(inputObj):
            inputObj[index] = sorter(element)

        try:
            inputObj.sort()
        except:
            pass

        return inputObj

    elif type(inputObj) is dict:
        return dict_sort(inputObj)

    else:
        return inputObj