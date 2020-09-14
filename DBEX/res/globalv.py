def version():
    with open("dbex/res/VERSION.txt") as file:
        return file.read()


__version__ = version()

header_shape = {
    "version": [int],
    "is_in_use": [bool],
    "file_hash": [str],
    "file_hash_algorithm": [str],
    "database_shape": [list, dict],
}