"""intlist_test.py
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from common.intlist import *

#
# Unit tests
#

class _TestMethods(_unittest.TestCase):
    def test_to_hstr(self):
        self.assertEqual(to_hstr([0xA]), '0A')
        self.assertEqual(to_hstr([0xA, 0x00]), '0A00')
        with self.assertRaises(TypeError):
            to_hstr(['A0'])
            to_hstr('A0')


if __name__ == '__main__':
    _unittest.main()
