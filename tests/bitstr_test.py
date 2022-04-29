"""test_bitstr.py
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from common.bitstr import *

#
# Unit tests
#

class _TestMethods(_unittest.TestCase):
    def test_clean(self):
        self.assertEqual(clean('0'), '0')
        self.assertEqual(clean('10'), '10')
        self.assertEqual(clean('11_00'), '1100')
        self.assertEqual(clean('01 10'), '0110')
        with self.assertRaises(TypeError):
            clean('0-')

    def test_to_hstr(self):
        self.assertEqual(to_hstr('1'), '1')
        self.assertEqual(to_hstr(' 10'), '2')
        self.assertEqual(to_hstr('1 0000'), '10')
        self.assertEqual(to_hstr('1 1_11'), 'F')
        with self.assertRaises(TypeError):
            to_hstr('1-')

    def test_xor(self):
        self.assertEqual(xor('1', '1'), '0')
        self.assertEqual(xor('10', '1'), '11')
        self.assertEqual(xor('10_00', ' 1'), '1001')
        with self.assertRaises(TypeError):
            xor('1-', '0')


if __name__ == '__main__':
    _unittest.main()
