#!/usr/bin/env python

"""
setup.py file for caffi
"""
import os
import sys
# Use setuptools to include build_sphinx, upload/sphinx commands
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if os.environ.get('NOLIBCA'):
    pkg_data = {}
else:
    pkg_data = {"caffi": ["lib/*/*"]}

# python 2/3 compatible way to load module from file
def load_module(name, location):
    if sys.hexversion < 0x03050000:
        import imp
        module = imp.load_source(name, location)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, location)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module

long_description = open('README.rst').read()

_version = load_module('_version','caffi/_version.py')

requirements = ['cffi>=1.3.0']
if sys.hexversion < 0x03040000:
    requirements.append('enum34')

setup(name='caffi',
      version=_version.__version__,
      description="""Channel Access Foreign Function Interface""",
      long_description=long_description,
      author="Xiaoqiang Wang",
      author_email="xiaoqiang.wang@psi.ch",
      url="https://github.com/CaChannel/caffi",
      packages=["caffi"],
      package_data=pkg_data,
      install_requires=requirements,
      license="BSD",
      platforms=["Windows", "Linux", "Mac OS X"],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   ],
      )
