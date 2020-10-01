def __sorter(inputObj: dict):
    # yapf: disable
    return {k: v for k, v in sorted(inputObj.items(), key=lambda item: item[1])}

def sorter(inputObj):
    if type(inputObj) is list:
        for index, element in enumerate(inputObj):
            inputObj[index] = sorter(element)

        try:
            inputObj.sort()
        except:
            pass
        return inputObj

    elif type(inputObj) is dict:
        return sorter(inputObj)

    else:
        return inputObj