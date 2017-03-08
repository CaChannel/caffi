#!/usr/bin/env python

"""
setup.py file for caffi
"""
import imp
# Use setuptools to include build_sphinx, upload/sphinx commands
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_description = open('README.rst').read()

_version = imp.load_source('_version','caffi/_version.py')

setup (name = 'caffi',
       version = _version.__version__,
       description = """Channel Access Foreign Function Interface""",
       long_description = long_description,
       author      = "Xiaoqiang Wang",
       author_email= "xiaoqiangwang@gmail.com",
       url         = "https://github.com/CaChannel/caffi",
       packages    = ["caffi"],
       package_data= {"caffi": ["lib/darwin-x86/*.dylib",
                                "lib/win32-x86/*.dll",
                                "lib/windows-x64/*.dll",
                                "lib/linux-x86/*.so",
                                "lib/linux-x86_64/*.so",]},
       install_requires = ['cffi>=0.8', 'enum34'],
       license     = "BSD",
       platforms   = ["Windows", "Linux", "Mac OS X"],
       classifiers = ['Development Status :: 4 - Beta',
                      'Environment :: Console',
                      'Intended Audience :: Developers',
                      'License :: OSI Approved :: BSD License',
                      'Programming Language :: Python :: 2',
                      'Programming Language :: Python :: 3',
                      ],
       )
