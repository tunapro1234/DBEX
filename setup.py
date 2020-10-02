from setuptools import setup

__version__ = "0.0.10.2"


def readMe():
    with open("README.md") as file:
        return file.read()


readme = readMe()

setup(
    name="dbex",
    license="MIT",
    zip_safe=False,
    packages=["dbex"],
    version=__version__,
    author="TUNAPRO1234",
    long_description=readme,
    include_package_data=True,
    author_email="tunagul54@gmail.com",
    url="https://github.com/tunapro1234/dbex/",
    description="json-like encoder and decoder",
    keywords=["json", "file", "encryption", "save", "data"],
    download_url="https://github.com/tunapro1234/DBEX/archive/v0.0.10.2.tar.gz",
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
    ],
)
