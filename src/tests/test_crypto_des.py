"""test_crypto_des.py
"""

# Standard library imports
import unittest

# Local application imports
from crypto.des import dea_e, dea_d, dea_ede_cbc, tdea_2_ede, tdea_2_ded, tdea_2_ede_ecb, tdea_2_ded_ecb, tdea_2_ede_cbc, tdea_2_ded_cbc, adjust_parity
from common.binary import HexString


#
# Test values
#
key4_0_to_7 = HexString('01234567')

key8_0_to_F = HexString('0123456789ABCDEF')
key8_0_to_F_1 = HexString('0123_4567_89AB_CDEF')
key8_0_to_F_5 = HexString('01234567_89ABCDEF')

key16_0_to_F_to_0 = HexString('0123456789ABCDEFFEDCBA9876543210')
key16_0_to_F_to_0_1 = HexString('0123456789ABCDEF_FEDCBA9876543210')

zeroes7 = HexString('00' * 7)
zeroes8 = HexString('00' * 8)
zeroes15 = HexString('00' * 15)
zeroes16 = HexString('00' * 16)

CC8 = HexString('CC' * 8)

FF8 = HexString('FF' * 8)
FF16 = HexString('FF' * 16)

fortyfour16 = HexString('44' * 16)


#
# Unit tests
#
class TestMethods(unittest.TestCase):
    """Unit tests for 'des' module
    """

    def test_dea_e(self):
        self.assertEqual(dea_e(key8_0_to_F, zeroes8),
                         'D5D44FF720683D0D')
        self.assertEqual(dea_e(key8_0_to_F_1, zeroes8),
                         'D5D44FF720683D0D')
        with self.assertRaises(ValueError):
            dea_e(key8_0_to_F, zeroes7)
        with self.assertRaises(ValueError):
            dea_e(key4_0_to_7, zeroes8)

    def test_dea_d(self):
        self.assertEqual(dea_d(key8_0_to_F, zeroes8),
                         '14AAD7F4DBB4E094')
        self.assertEqual(dea_d(key8_0_to_F_1, zeroes8),
                         '14AAD7F4DBB4E094')

    def test_dea_ede_cbc(self):
        self.assertEqual(dea_ede_cbc(key8_0_to_F, fortyfour16, zeroes8),
                         '8850517E7A817B1EBA5E2B72B6217B50')
        self.assertEqual(dea_ede_cbc(key8_0_to_F_5, fortyfour16, CC8),
                         'F31C939892FEFC8F14DBA3B2C7BAF0A7')
        with self.assertRaises(ValueError):
            dea_ede_cbc(key8_0_to_F, zeroes15, zeroes8)
        with self.assertRaises(ValueError):
            dea_ede_cbc(key8_0_to_F, zeroes16, zeroes7)

    def test_tdea_2_ede(self):
        self.assertEqual(tdea_2_ede(key16_0_to_F_to_0, zeroes8),
                         '08D7B4FB629D0885')
        self.assertEqual(tdea_2_ede(key16_0_to_F_to_0_1, zeroes8),
                         '08D7B4FB629D0885')

    def test_tdea_2_ded(self):
        self.assertEqual(tdea_2_ded(key16_0_to_F_to_0, zeroes8),
                         'C1E6E95D2166B5C4')
        self.assertEqual(tdea_2_ded(key16_0_to_F_to_0_1, zeroes8),
                         'C1E6E95D2166B5C4')

    def test_tdea_2_ede_ecb(self):
        self.assertEqual(tdea_2_ede_ecb(HexString('F19DADD9AEA429D92FB5F7B92A15FD04'),
                         HexString('01234567899876543210012345678998')),
                         '7E3F0B0E968FA631C8E4618CA317256A')
        self.assertEqual(tdea_2_ede_ecb(HexString('F19DADD9AEA429D92FB5F7B92A15FD04'),
                         HexString('01017391010101101320010101010101')),
                         '0AA72BC2B91EFDCFFFD0EDD21A03F200')

    def test_tdea_2_ded_ecb(self):
        self.assertEqual(tdea_2_ded_ecb(HexString('F19DADD9AEA429D92FB5F7B92A15FD04'),
                         HexString('7E3F0B0E968FA631C8E4618CA317256A')),
                         '01234567899876543210012345678998')
        self.assertEqual(tdea_2_ded_ecb(HexString('F19DADD9AEA429D92FB5F7B92A15FD04'),
                         HexString('0AA72BC2B91EFDCFFFD0EDD21A03F200')),
                         '01017391010101101320010101010101')

    def test_tdea_2_ede_cbc(self):
        self.assertEqual(tdea_2_ede_cbc(key16_0_to_F_to_0, zeroes16, zeroes8),
                         '08D7B4FB629D08850A121DC33DFB5947')
        self.assertEqual(tdea_2_ede_cbc(key16_0_to_F_to_0_1, zeroes16, FF8),
                         '847CA792BFA6FD4C9154099C397A0ABA')
        with self.assertRaises(ValueError):
            tdea_2_ede_cbc(key16_0_to_F_to_0, zeroes15, zeroes8)
        with self.assertRaises(ValueError):
            tdea_2_ede_cbc(key16_0_to_F_to_0, zeroes16, zeroes7)

    def test_tdea_2_ded_cbc(self):
        self.assertEqual(tdea_2_ded_cbc(key16_0_to_F_to_0, zeroes16, zeroes8),
                         'C1E6E95D2166B5C4C1E6E95D2166B5C4')
        self.assertEqual(tdea_2_ded_cbc(key16_0_to_F_to_0_1, zeroes16, FF8),
                         '3E1916A2DE994A3BC1E6E95D2166B5C4')
        with self.assertRaises(ValueError):
            tdea_2_ded_cbc(key16_0_to_F_to_0, zeroes15, zeroes8)
        with self.assertRaises(ValueError):
            tdea_2_ded_cbc(key16_0_to_F_to_0, zeroes16, zeroes7)

    def test_adjust_parity(self):
        self.assertEqual(adjust_parity(key16_0_to_F_to_0), key16_0_to_F_to_0)
        self.assertEqual(adjust_parity(HexString('462EC416E0E83C04_2CD1B10731AB4736')),
                         '462FC416E0E93D042CD0B00731AB4637')


if __name__ == '__main__':
    unittest.main()
