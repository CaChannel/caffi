#!/usr/bin/env bash
if [[ `uname` == "Darwin" ]]; then
    clang -dynamiclib cawrapper.c -o libcawrapper.dylib
else
    gcc -fPIC -shared cawrapper.c -o libcawrapper.so
fi
