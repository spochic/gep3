"""test_str.py
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from str import *

#
# Unit tests
#

class _TestMethods(_unittest.TestCase):
    def test_perm(self):
        self.assertEqual(perm('FEDCBA9876543210', [
                         16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]), '0123456789ABCDEF')


if __name__ == '__main__':
    _unittest.main()
