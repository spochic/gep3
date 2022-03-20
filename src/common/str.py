"""str.py

Generic functions working on strings
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports


def perm(str_in, permutation):
    """perm():
    """
    str_out = ''

    for i in permutation:
        str_out += str_in[i-1]

    return str_out


def exp(str_in, expansion):
    """exp():
    """
    return perm(str_in, expansion)


def lcs(str_in, shift):
    """lcs():
    """
    return str_in[shift:] + str_in[:shift]


def to_ascii(str_in):
    return ''.join([F"{ord(c):02X}" for c in str_in])

#
# Unit tests
#


class _TestMethods(_unittest.TestCase):
    def test_perm(self):
        self.assertEqual(perm('FEDCBA9876543210', [
                         16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]), '0123456789ABCDEF')


if __name__ == '__main__':
    _unittest.main()
