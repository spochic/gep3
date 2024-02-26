"""parserc.py: Parser Combinators
"""
# Standard library imports

# Third party imports
from parsec import parsecmap, desc, regex, string, joint as __joint, generate, one_of, exclude, many, count

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
    return parsecmap(__joint(*p), flatten)


# Generic parsers
nibble = desc(regex(r'[0-9a-zA-Z]'), 'nibble')
byte = desc(regex(r'[0-9a-zA-Z]{2}'), 'byte')
null = desc(string('00'), 'null')
