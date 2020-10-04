from setuptools import setup
from Cython.Build import cythonize

file = "decoder_cy"
setup(ext_modules=cythonize(f"dbex/cython/{file}/{file}.pyx", annotate=True),
      #   build_dir=f"dbex/cython/{file}",
      )
