from setuptools import setup


def version():
	with open("dbex/res/VERSION.txt") as file:
		return file.read()


__version__ = version()

setup(
	name="DATABASE EXTENDED",
	version="0.9.12",
	description="json-like encoder and decoder",	
	url="https://github.com/tunapro1234/dbex/",
	author="TUNAPRO1234",
	author_email="tunagul54@gmail.com",
	license="GNU General Public License v3.0",
	packages=["dbex"],
	include_package_data=True,
	zip_safe=False,
)
