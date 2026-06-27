from Cython.Build import cythonize
from setuptools import setup, Extension
import numpy

ext_modules = cythonize(
    ["scripts/*.pyx", "scripts/*.py"],
    language_level="3",
    compiler_directives={
        "boundscheck": False,
        "wraparound": False,
        "cdivision": True,
    },
)

# Add numpy include dirs for scripts that use numpy
for ext in ext_modules:
    ext.include_dirs.append(numpy.get_include())

setup(
    name="prima-scripts",
    ext_modules=ext_modules,
    zip_safe=False,
)
