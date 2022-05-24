"""key_management_test.py
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from emv.key_management import *

#
# Unit tests
#

class _TestMethods(_unittest.TestCase):
    def test_master_key_derivation_A(self):
        self.assertEqual(master_key_derivation_A('01234567899876543210012345678998', '5413123456784800', '00'), 'A3D0BC420A766611F7BC19E7F2E221AF')
        self.assertEqual(master_key_derivation_A('01234567899876543210012345678998', '5413123456784808', '00'), '462EC416E0E83C042CD1B10731AB4736')
        self.assertEqual(master_key_derivation_A('01017391010101101320010101010101', '4012340000000016', '00'), '9991C31043BFD9858016396CF24F0D6F')

if __name__ == '__main__':
    _unittest.main()
