"""
Compatible layer for Python 2 and 3
"""
import sys

__all__ = ['basestring', 'to_bytes', 'to_string']

if sys.hexversion >= 0x03000000:
    basestring = (str, bytes)
else:
    basestring = str


def to_bytes(str_val):
    if isinstance(str_val, bytes):
        return str_val

    if sys.hexversion >= 0x03000000:
        return str_val.encode('utf8')
    else:
        return str(str_val)


def to_string(bytes_val):
    if isinstance(bytes_val, str):
        return bytes_val

    if sys.hexversion >= 0x03000000:
        return bytes_val.decode('utf8')
    else:
        return str(bytes_val)
