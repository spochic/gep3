"""records_test.py
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from emv.records import *

#
# Unit tests
#

class _TestMethods(_unittest.TestCase):
    def test_decode_afl(self):
        self.assertEqual(decode_afl('0801010010010100'), ([(1, 1, 1, 0), (2, 1, 1, 0)], None))
        self.assertEqual(decode_afl('0801010110010100'), ([(1, 1, 1, 1), (2, 1, 1, 0)], None))
        self.assertEqual(decode_afl('080202001801030110010300'), ([(1, 2, 2, 0), (3, 1, 3, 1), (2, 1, 3, 0)], None))


if __name__ == '__main__':
    _unittest.main()
