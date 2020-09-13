from dbex.lib.encryption import encrypter as defaultEncrypter_func


def version():
    with open("dbex/res/VERSION.txt") as file:
        return file.read()


__version__ = version()


class Encoder:
    encrypter_func = defaultEncrypter_func

    @staticmethod
    def __dump_gen_(obj,
                    max_gen_lvl=1,
                    gen_lvl=1,
                    indent="",
                    seperators=(", ", ": ")):
        if type(seperators) != tuple:
            raise Exception("Seperator error")

        parser1 = seperators[0].rstrip() if indent else seperators[0]
        parser2 = seperators[1]

        if type(obj) in [list, tuple]:
            first = True
            yield "(" if type(obj) == tuple else "["

            for element in obj:
                if not first:
                    yield parser1 + "\n" + indent * (gen_lvl +
                                                     1) if indent else parser1

                elif indent:
                    yield "\n" + indent * (gen_lvl + 1)

                for i in Encoder.__dump_gen(element, max_gen_lvl, gen_lvl + 1,
                                            indent):
                    yield i

                first = False

            if indent:
                yield "\n" + indent * gen_lvl
            yield ")" if type(obj) == tuple else "]"

        elif type(obj) == dict:
            yield "{"
            first = True

            for key, value in obj.items():
                if not first:
                    yield parser1 + "\n" + indent * (gen_lvl +
                                                     1) if indent else parser1

                elif indent:
                    yield "\n" + indent * (gen_lvl + 1)

                # key döndürme
                yield "".join([
                    i
                    for i in Encoder.__dump_gen_(key, max_gen_lvl, gen_lvl, "")
                ]) if type(key) == tuple else Encoder.__convert(key)
                yield parser2

                # value döndürme
                for i in Encoder.__dump_gen(value, max_gen_lvl, gen_lvl + 1,
                                            indent):
                    yield i

                first = False

            if indent:
                yield "\n" + indent * gen_lvl
            yield "}"

        else:
            yield obj

    @staticmethod
    def __dump_gen(element,
                   max_gen_lvl=0,
                   gen_lvl=0,
                   indent=0,
                   seperators=(", ", ": ")):
        indent = " " * indent if type(indent) == int else indent

        if type(element) in [tuple, list, dict]:
            if gen_lvl < max_gen_lvl:
                for i in Encoder.__dump_gen_(element, max_gen_lvl, gen_lvl,
                                             indent, seperators):
                    yield i
            else:
                yield "".join([
                    i for i in Encoder.__dump_gen_(element, max_gen_lvl,
                                                   gen_lvl, indent, seperators)
                ])
        else:
            yield Encoder.__convert(element)

    @staticmethod
    def __convert(element):
        if element in [float("Infinity"),
                       float("-Infinity")] or element != element:
            if element == float("Infinity"):
                return "Infinity"
            elif element == float("-Infinity"):
                return "-Infinity"
            elif element != element:
                return "NaN"
        else:
            return f'"{element}"' if type(element) == str else str(element)

    @staticmethod
    def sort_keys(rv, *args, **kwargs):
        return rv

    @staticmethod
    def dumps(obj, sort_keys=0, **kwargs):
        if sort_keys:
            return Encoder.sort_keys("".join(
                [i for i in Encoder.__dump_gen(obj, **kwargs)]))
        else:
            return "".join([i for i in Encoder.__dump_gen(obj, **kwargs)])

    @staticmethod
    def dumps(obj,
              max_gen_lvl=0,
              indent=0,
              seperators=(", ", ": "),
              sort_keys=0):
        if sort_keys:
            return Encoder.sort_keys("".join([
                i for i in Encoder.__dump_gen(
                    obj, max_gen_lvl=0, indent=0, seperators=(", ", ": "))
            ]))
        else:
            return "".join([
                i for i in Encoder.__dump_gen(
                    obj, max_gen_lvl=0, indent=0, seperators=(", ", ": "))
            ])

    @staticmethod
    def dump(obj, file_path, **kwargs):
        Encoder.write(file_path, Encoder.encrypter_func(dumps(obj, **kwargs)))

    @staticmethod
    def write(rv, *args, **kwargs):
        return rv


def test():
    return


if __name__ == "__main__":
    test()