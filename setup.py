from setuptools import setup

def readme():
    with open("README.txt") as f:
        return f.read()


setup(
    name="DATABASE EXTENDED",
    version="0.8.2",
    description="tunapro1",
    long_description=readme(),
    url="http://github.com/FRC7839/NightVision/",
    author="TUNAPRO1234",
    author_email="tunagul54@gmail.com",
    license="GNU General Public License v3.0",
    packages=["dbex"],
    include_package_data=True,
    zip_safe=False,
)
