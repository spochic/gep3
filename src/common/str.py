"""str.py

Generic functions working on strings
"""

# Standard library imports

# Third party imports

# Local application imports


def perm(str_in: str, permutation: list[int]) -> str:
    """perm():
    """
    str_out = ''

    for i in permutation:
        str_out += str_in[i-1]

    return str_out


def exp(str_in: str, expansion: list[int]) -> str:
    """exp():
    """
    return perm(str_in, expansion)


def lcs(str_in: str, shift: int) -> str:
    """lcs():
    """
    return str_in[shift:] + str_in[:shift]


def to_ascii(str_in: str) -> str:
    return ''.join([F"{ord(c):02X}" for c in str_in])


def clean(str_in: str, keep_char='', remove_char='', command_name='()', str_name='') -> str:
    """clean(str)

    - Removes '_' characters
    - Raises exceptions on illegal characters
    """
    str_out = ''
    for nibble in str_in:
        if nibble in keep_char:
            str_out += nibble
        elif nibble in remove_char:
            pass
        else:
            if str_name == '':
                raise TypeError(F"{command_name}: Unknown nibble: {nibble}")
            else:
                raise TypeError(
                    F"{command_name}: Unknown nibble in {str_name}: {nibble}")

    return str_out
