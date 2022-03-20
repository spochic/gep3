"""hstr.py

Generic functions working on strings containing only
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F', 'a', 'b', 'c', 'd', 'e', 'f',
    ' ', and '_' characters
"""

# Standard library imports
import unittest as _unittest

# Third party imports

# Local application imports


def clean(hstr_in: str, command_name='()', hstr_name='') -> str:
    """clean(hstr)

    - Capitalizes hexadecimal digits
    - Removes ' ' and '_' characters
    - Raises exceptions on not allowed characters
    """
    hstr_out = ''
    for nibble in hstr_in:
        if nibble in '0123456789ABCDEFabcdef':
            hstr_out += nibble.capitalize()
        elif nibble in ' _':
            pass
        else:
            if hstr_name == '':
                raise TypeError(F"{command_name}: Unknown nibble: {nibble}")
            else:
                raise TypeError(
                    F"{command_name}: Unknown nibble in {hstr_name}: {nibble}")

    return hstr_out


def to_bitstr(hstr: str, command_name='()', hstr_name='') -> str:
    """to_bitstr(hstr): converts 'hex strings' to 'bit strings'
    """
    bstr = ''

    for nibble in clean(hstr, command_name, hstr_name):
        bstr += F"{int(nibble, 16):04b}"

    return bstr


def xor(hstr_a: str, hstr_b: str, command_name='()', hstr_name='') -> str:
    """xor(hstr_a, hstr_b):
    """
    hstr_a = clean(hstr_a, command_name, hstr_name)
    hstr_b = clean(hstr_b, command_name, hstr_name)
    length = max(len(hstr_a), len(hstr_b))
    hstr_a = hstr_a.rjust(length, '0')
    hstr_b = hstr_b.rjust(length, '0')
    xor_hstr = ''

    for (nibble_a, nibble_b) in zip(hstr_a, hstr_b):
        xor_hstr += F"{int(nibble_a, 16)^int(nibble_b, 16):X}"

    return xor_hstr


def not_hstr(hstr_in: str, command_name='()', hstr_name='') -> str:
    """not(hstr):
    """
    hstr_in = clean(hstr_in, command_name, hstr_name)
    hstr_out = ''

    for nibble in hstr_in:
        hstr_out += xor(nibble, 'F')

    return hstr_out


def to_dec(hstr: str, command_name='()', hstr_name='') -> int:
    """to_dec():
    """
    return int(clean(hstr, command_name, hstr_name), 16)


def to_intlist(hstr: str, command_name='()', hstr_name='') -> []:
    """to_intlist():
    """
    hstr = clean(hstr, command_name, hstr_name)
    if (len(hstr) % 2) != 0:
        raise ValueError(
            F"{command_name}: uneven length for {hstr_name}: {len(hstr)}")

    bytelist = []
    for i in range(len(hstr)//2):
        bytelist.append(int(hstr[i*2:(i+1)*2], 16))

    return bytelist


def minimum(hstr_a: str, hstr_b: str) -> str:
    """minimum():
    """
    hstr_a = clean(hstr_a)
    hstr_b = clean(hstr_b)

    if int(hstr_a, 16) == min(int(hstr_a, 16), int(hstr_b, 16)):
        return hstr_a

    return hstr_b

#
# Unit tests
#


class _TestMethods(_unittest.TestCase):
    def test_clean(self):
        self.assertEqual(clean('A'), 'A')
        self.assertEqual(clean('A0'), 'A0')
        self.assertEqual(clean('AA_BB'), 'AABB')
        self.assertEqual(clean('AA BB'), 'AABB')
        self.assertEqual(clean('a'), 'A')
        self.assertEqual(clean('a0'), 'A0')
        self.assertEqual(clean('aa_bb'), 'AABB')
        self.assertEqual(clean('aa bb'), 'AABB')
        with self.assertRaises(TypeError):
            clean('F-')

    def test_to_bitstr(self):
        self.assertEqual(to_bitstr('A'), '1010')
        self.assertEqual(to_bitstr('f_0'), '11110000')
        self.assertEqual(to_bitstr(' 1 B'), '00011011')
        self.assertEqual(to_bitstr('F F_Ff'), '1111111111111111')
        with self.assertRaises(TypeError):
            to_bitstr('F-')

    def test_xor(self):
        self.assertEqual(xor('5', 'b'), 'E')

    def test_not(self):
        self.assertEqual(not_hstr('5'), 'A')

    def test_to_dec(self):
        self.assertEqual(to_dec('F F_fF'), 65535)

    def test_to_intlist(self):
        self.assertEqual(to_intlist('03'), [0x03])
        self.assertEqual(to_intlist('03AB'), [0x03, 0xAB])
        self.assertEqual(to_intlist('03_AB'), [0x03, 0xAB])
        self.assertEqual(to_intlist(' 03_AB'), [0x03, 0xAB])
        with self.assertRaises(TypeError):
            to_intlist('F-')
        with self.assertRaises(ValueError):
            to_intlist('123')

    def test_minimum(self):
        self.assertEqual(minimum('0', 'A'), '0')
        self.assertEqual(minimum('10', 'A'), 'A')
        self.assertEqual(minimum('FF', 'FF'), 'FF')
        self.assertEqual(minimum('F', '10'), 'F')


if __name__ == '__main__':
    _unittest.main()
