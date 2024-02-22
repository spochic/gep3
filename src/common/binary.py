"""binary.py
"""
# Standard library imports
from collections import UserString
import math
import operator
from typing import Callable, Self, Iterable

# Third party imports

# Local application imports


# Helper functions
__HEX_DIGITS = '0123456789abcdefABCDEF'
__WHITESPACE = '_'


def clean_hex_char(c: str) -> str:
    match c:
        case c if c in __HEX_DIGITS:
            return c
        case c if c in __WHITESPACE:
            return ''
        case _:
            raise TypeError(
                F"Character '{c}' not allowed in hexadecimal string")


def bitwise_operation(left: str, right: str, operator: Callable[[int, int], int]):
    length = max(len(left), len(right))

    return format(operator(int(left, 16), int(right, 16)), F"0{length}X")


# 'HexString' class
class HexString(UserString):
    def __init__(self, string: str):
        value: str = ''.join(map(clean_hex_char, string))
        super().__init__(value.upper())

    @property
    def bytes(self) -> bytes:
        return bytes.fromhex(self.data)

    @property
    def byte_length(self) -> int:
        if len(self) % 2 == 0:
            return len(self) // 2
        else:
            raise ValueError(F"{self.data} has an odd number of nibbles")

    @property
    def bit_string(self) -> str:
        return ''.join([F"{int(nibble, 16):04b}" for nibble in self.data])

    @property
    def bit_length(self) -> int:
        return len(self) * 4

    @property
    def int_list(self) -> list[int]:
        return list(self.bytes)

    @property
    def dscan_decimalize(self) -> str:
        """dscan_decimalize: double scan decimalization
        """
        dstr1 = ''
        dstr2 = ''
        for h in self.data:
            if h.isdigit():
                dstr1 = dstr1 + h
            else:
                dstr2 = dstr2 + F"{int(h, 16)-10}"

        return dstr1 + dstr2

    def blocks(self, bytesize: int) -> Iterable[Self]:
        nr_blocks = math.ceil(self.byte_length / bytesize)
        return (self[i*2*bytesize:(i+1)*2*bytesize] for i in range(nr_blocks))

    def join(self, seq: Iterable[Self]):
        return self + ''.join([hstr.data for hstr in seq])

    def __or__(self, other: Self):
        return HexString(bitwise_operation(self.data, other.data, operator.__or__))

    def __xor__(self, other: Self):
        return HexString(bitwise_operation(self.data, other.data, operator.__xor__))

    def __and__(self, other: Self):
        return HexString(bitwise_operation(self.data, other.data, operator.__and__))

    def __invert__(self):
        return self ^ HexString('FF' * self.byte_length)
