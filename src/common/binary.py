"""binary.py
"""
# Standard library imports
from __future__ import annotations
from collections import UserString
import math
import operator
from typing import Callable, Iterable

# Third party imports

# Local application imports


# Helper functions
__HEX_DIGITS = '0123456789abcdefABCDEF'
__BIT_DIGITS = '01'
__WHITESPACE = '_'


def clean_char(c: str, keep: str, ignore: str, message: str) -> str:
    match c:
        case c if c in keep:
            return c
        case c if c in ignore:
            return ''
        case _:
            raise TypeError(
                F"Character '{c}' not allowed in {message}")


def clean_hex_char(c: str) -> str:
    return clean_char(c, keep=__HEX_DIGITS, ignore=__WHITESPACE, message="hexadecimal string")


def clean_bit_char(c: str) -> str:
    return clean_char(c, keep=__BIT_DIGITS, ignore=__WHITESPACE, message="binary string")


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
    def bit_string(self) -> BitString:
        return BitString(''.join([F"{int(nibble, 16):04b}" for nibble in self.data]))

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

    def blocks(self, bytesize: int) -> Iterable[HexString]:
        nr_blocks = math.ceil(self.byte_length / bytesize)
        return (self[i*2*bytesize:(i+1)*2*bytesize] for i in range(nr_blocks))

    def join(self, seq: Iterable[HexString]):
        return self + ''.join([hstr.data for hstr in seq])

    def __or__(self, other: HexString):
        return HexString(bitwise_operation(self.data, other.data, operator.__or__))

    def __xor__(self, other: HexString):
        return HexString(bitwise_operation(self.data, other.data, operator.__xor__))

    def __and__(self, other: HexString):
        return HexString(bitwise_operation(self.data, other.data, operator.__and__))

    def __invert__(self):
        return self ^ HexString('FF' * self.byte_length)


# 'BitString' class
class BitString(UserString):
    def __init__(self, string: str):
        value: str = ''.join(map(clean_bit_char, string))
        super().__init__(value.upper())

    @property
    def bytes(self) -> bytes:
        return HexString(self.data).bytes

    @property
    def byte_length(self) -> int:
        return HexString(self.data).byte_length

    @property
    def hex_string(self) -> HexString:
        if len(self) % 4 == 0:
            return HexString(format(int(self.data, 2), F"0{len(self)//4}X"))
        else:
            raise ValueError(
                F"{self.data} has a number of bit that is not a multiple of 4")

    @property
    def int_list(self) -> list[int]:
        return HexString(self.data).int_list

    def blocks(self, bitsize: int) -> Iterable[BitString]:
        nr_blocks = math.ceil(self.byte_length / bitsize)
        return (self[i*2*bitsize:(i+1)*2*bitsize] for i in range(nr_blocks))

    def join(self, seq: Iterable[BitString]):
        return self + ''.join([bstr.data for bstr in seq])

    def permute(self, permutation: list[int]) -> BitString:
        str_out = BitString('')

        for i in permutation:
            str_out += self[i-1]

        return str_out

    def expand(self, expansion: list[int]) -> BitString:
        return self.permute(expansion)

    def left_circular_shit(self, shift: int) -> BitString:
        return self[shift:] + self[:shift]

    def __or__(self, other: BitString) -> BitString:
        return BitString(bitwise_operation(self.data, other.data, operator.__or__))

    def __xor__(self, other: BitString) -> BitString:
        return BitString(bitwise_operation(self.data, other.data, operator.__xor__))

    def __and__(self, other: BitString) -> BitString:
        return BitString(bitwise_operation(self.data, other.data, operator.__and__))

    def __invert__(self) -> BitString:
        return self ^ BitString('1' * len(self))
