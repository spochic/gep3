"""dsc_test.py
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports
from emv.dsc import *

#
# Unit tests
#

class _TestMethods(_unittest.TestCase):
    def test_generate_ivcvc3(self):
        self.assertEqual(generate_ivcvc3('A3D0BC420A766611F7BC19E7F2E221AF', '5413123456784800D20061019000990000000F'), 'A46B')

    def test_generate_cvc3(self):
        self.assertEqual(generate_cvc3('A3D0BC420A766611F7BC19E7F2E221AF', 'A46B00000899005E'), '30687')

    def test_generate_dcvv(self):
        self.assertEqual(generate_dcvv('9991C31043BFD9858016396CF24F0D6F', '4012340000000016', '0001', '1228'), '369')
        self.assertEqual(generate_dcvv('1274FB0FCD3E27E088B741553037F089', '4761739001010010', '0001', '1220'), '802')

if __name__ == '__main__':
    _unittest.main()
