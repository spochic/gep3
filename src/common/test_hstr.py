"""test_hstr.py
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from hstr import * 

#
# Unit tests
#

class _TestMethods(_unittest.TestCase):
    def test_clean(self):
        self.assertEqual(clean('A'), 'A')
        self.assertEqual(clean('A0'), 'A0')
        self.assertEqual(clean('AA_BB'), 'AABB')
        self.assertEqual(clean('a'), 'A')
        self.assertEqual(clean('a0'), 'A0')
        self.assertEqual(clean('aa_bb'), 'AABB')
        with self.assertRaises(TypeError):
            clean('F-')
        with self.assertRaises(TypeError):
            clean('aa bb')

    def test_to_bitstr(self):
        self.assertEqual(to_bitstr('A'), '1010')
        self.assertEqual(to_bitstr('f_0'), '11110000')
        self.assertEqual(to_bitstr('FF_Ff'), '1111111111111111')
        with self.assertRaises(TypeError):
            to_bitstr('F-')
        with self.assertRaises(TypeError):
            to_bitstr(' 1 B')

    def test_xor(self):
        self.assertEqual(xor('5', 'b'), 'E')

    def test_not(self):
        self.assertEqual(not_hstr('5'), 'A')

    def test_to_dec(self):
        self.assertEqual(to_dec('FF_fF'), 65535)

    def test_to_intlist(self):
        self.assertEqual(to_intlist('03'), [0x03])
        self.assertEqual(to_intlist('03AB'), [0x03, 0xAB])
        self.assertEqual(to_intlist('03_AB'), [0x03, 0xAB])
        with self.assertRaises(TypeError):
            to_intlist('F-')
        with self.assertRaises(TypeError):
            to_intlist(' 03_AB')
        with self.assertRaises(ValueError):
            to_intlist('123')

    def test_minimum(self):
        self.assertEqual(minimum('0', 'A'), '0')
        self.assertEqual(minimum('10', 'A'), 'A')
        self.assertEqual(minimum('FF', 'FF'), 'FF')
        self.assertEqual(minimum('F', '10'), 'F')


if __name__ == '__main__':
    _unittest.main()
