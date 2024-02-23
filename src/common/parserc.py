"""parserc.py: Parser Combinators
"""
# Standard library imports

# Third party imports
import parsec
from parsec import *

# Local application imports


#
# Definitions
#
# Helper functions
def flatten(iter):
    return ''.join(iter)


# Overloaded parsec functions
# def count(p, n):
#     return parsec.parsecmap(parsec.count(p, n), flatten)


# def many(p):
#     return parsec.parsecmap(parsec.many(p), flatten)


def joint(*p):
    return parsec.parsecmap(parsec.joint(*p), flatten)


# Generic parsers
nibble = parsec.desc(parsec.regex(r'[0-9a-zA-Z]'), 'nibble')
byte = parsec.desc(parsec.regex(r'[0-9a-zA-Z]{2}'), 'byte')
null = parsec.desc(parsec.string('00'), 'null')
