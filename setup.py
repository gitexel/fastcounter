#!/usr/bin/env python
import setuptools
from Cython.Build import cythonize

setuptools.setup(
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    package_data={"fastcounter": ["py.typed"]},
    ext_modules=cythonize('fastcounter/__init__.py'),
)
