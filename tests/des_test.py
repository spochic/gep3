"""test_des.py
"""

# Standard library imports
import unittest as _unittest

# Local application imports
from crypto.des import *

#
# Unit tests
#

class TestMethods(_unittest.TestCase):
    """Unit tests for 'des' module
    """

    def test_dea_e(self):
        self.assertEqual(dea_e('0123456789ABCDEF', '00' * 8), 'D5D44FF720683D0D')
        self.assertEqual(dea_e('0123_4567_89AB_CDEF', '00' * 8), 'D5D44FF720683D0D')
        with self.assertRaises(TypeError):
            dea_e('0123-4567-89AB-CDEF', '00' * 8)
            dea_e('0123456789ABCDEF', '00' * 7)
            dea_e('01234567', '00' * 8)
            dea_e('0123 4567 89AB CDEF', '00' * 8)

    def test_dea_d(self):
        self.assertEqual(dea_d('0123456789ABCDEF', '00' * 8), '14AAD7F4DBB4E094')
        self.assertEqual(dea_d('0123_4567_89AB_CDEF', '00' * 8), '14AAD7F4DBB4E094')
        with self.assertRaises(TypeError):
            dea_d('0123-4567-89AB-CDEF', '00' * 8)
            dea_d('0123 4567 89AB CDEF', '00' * 8)

    def test_dea_ede_cbc(self):
        self.assertEqual(dea_ede_cbc('0123456789ABCDEF', '44' * 16, '00' * 8), '8850517E7A817B1EBA5E2B72B6217B50')
        self.assertEqual(dea_ede_cbc('01234567_89ABCDEF', '44' * 16, 'CC' * 8), 'F31C939892FEFC8F14DBA3B2C7BAF0A7')
        with self.assertRaises(TypeError):
            dea_ede_cbc('0123456789ABCDEF', '00' * 15, '00' * 8)
            dea_ede_cbc('0123456789ABCDEF', '00' * 16, '00' * 7)
            dea_ede_cbc('01234567 89ABCDEF', 'FF' * 16, '00' * 8)

    def test_tdea_2_ede(self):
        self.assertEqual(tdea_2_ede('0123456789ABCDEFFEDCBA9876543210', '00' * 8), '08D7B4FB629D0885')
        self.assertEqual(tdea_2_ede('0123456789ABCDEF_FEDCBA9876543210', '00' * 8), '08D7B4FB629D0885')
        with self.assertRaises(TypeError):
            tdea_2_ede('0123-4567-89AB-CDEF', '00' * 8)
            tdea_2_ede('0123456789ABCDEF FEDCBA9876543210', '00' * 8)

    def test_tdea_2_ded(self):
        self.assertEqual(tdea_2_ded('0123456789ABCDEFFEDCBA9876543210', '00' * 8), 'C1E6E95D2166B5C4')
        self.assertEqual(tdea_2_ded('0123456789ABCDEF_FEDCBA9876543210', '00' * 8), 'C1E6E95D2166B5C4')
        with self.assertRaises(TypeError):
            tdea_2_ded('0123-4567-89AB-CDEF', '00' * 8)
            tdea_2_ded('0123456789ABCDEF FEDCBA9876543210', '00' * 8)

    def test_tdea_2_ede_ecb(self):
        self.assertEqual(tdea_2_ede_ecb('F19DADD9AEA429D92FB5F7B92A15FD04', '01234567899876543210012345678998'), '7E3F0B0E968FA631C8E4618CA317256A')
        self.assertEqual(tdea_2_ede_ecb('F19DADD9AEA429D92FB5F7B92A15FD04', '01017391010101101320010101010101'), '0AA72BC2B91EFDCFFFD0EDD21A03F200')

    def test_tdea_2_ded_ecb(self):
        self.assertEqual(tdea_2_ded_ecb('F19DADD9AEA429D92FB5F7B92A15FD04', '7E3F0B0E968FA631C8E4618CA317256A'), '01234567899876543210012345678998')
        self.assertEqual(tdea_2_ded_ecb('F19DADD9AEA429D92FB5F7B92A15FD04', '0AA72BC2B91EFDCFFFD0EDD21A03F200'), '01017391010101101320010101010101')

    def test_tdea_2_ede_cbc(self):
        self.assertEqual(tdea_2_ede_cbc('0123456789ABCDEFFEDCBA9876543210', '00' * 16, '00' * 8), '08D7B4FB629D08850A121DC33DFB5947')
        self.assertEqual(tdea_2_ede_cbc('0123456789ABCDEF_FEDCBA9876543210', '00' * 16, 'FF' * 8), '847CA792BFA6FD4C9154099C397A0ABA')
        with self.assertRaises(TypeError):
            tdea_2_ede_cbc('0123456789ABCDEFFEDCBA9876543210', '00' * 15, '00' * 8)
            tdea_2_ede_cbc('0123456789ABCDEFFEDCBA9876543210', '00' * 16, '00' * 7)
            tdea_2_ede_cbc('0123456789ABCDEF FEDCBA9876543210', 'FF' * 16, '00' * 8)

    def test_tdea_2_ded_cbc(self):
        self.assertEqual(tdea_2_ded_cbc('0123456789ABCDEFFEDCBA9876543210', '00' * 16, '00' * 8), 'C1E6E95D2166B5C4C1E6E95D2166B5C4')
        self.assertEqual(tdea_2_ded_cbc('0123456789ABCDEF_FEDCBA9876543210', '00' * 16, 'FF' * 8), '3E1916A2DE994A3BC1E6E95D2166B5C4')
        with self.assertRaises(TypeError):
            tdea_2_ded_cbc('0123456789ABCDEFFEDCBA9876543210', '00' * 15, '00' * 8)
            tdea_2_ded_cbc('0123456789ABCDEFFEDCBA9876543210', '00' * 16, '00' * 7)
            tdea_2_ded_cbc('0123456789ABCDEF FEDCBA9876543210', 'FF' * 16, '00' * 8)

    def test_adjust_parity(self):
        self.assertEqual(adjust_parity('0123456789ABCDEFFEDCBA9876543210'), '0123456789ABCDEFFEDCBA9876543210')
        self.assertEqual(adjust_parity('462EC416E0E83C04_2CD1B10731AB4736'), '462FC416E0E93D042CD0B00731AB4637')

if __name__ == '__main__':
    _unittest.main()
