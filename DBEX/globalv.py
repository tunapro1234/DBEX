def version():
    # with open("VERSION.txt") as file:
    # 	return file.read()
    version = "0.1.10"
    return version


__version__ = version()

header_shape = {
    "version": [int],
    "is_in_use": [bool],
    "file_hash": [str],
    "file_hash_algorithm": [str],
    "database_shape": [list, dict],
}