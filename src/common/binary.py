"""binary.py
"""
# Standard library imports
from __future__ import annotations
from collections import UserString
from collections.abc import Sequence
import math
from typing import Iterable, SupportsInt
from functools import reduce
from operator import __add__, __xor__, __and__, __or__, __lshift__, __rshift__
import sys as _sys
from array import array

# Third party imports

# Local application imports


# Helper functions
__HEX_DIGITS = '0123456789abcdefABCDEF'
__BIT_DIGITS = '01'


def _clean_char(keep: str, ignore: str, message: str):
    def _clean_char(c: str):
        if c in keep:
            return c
        elif c in ignore:
            return ''
        else:
            raise TypeError(F"Character '{c}' not allowed in {message}")

    return _clean_char


def _clean_string(s: str, keep: str, ignore: str, message: str) -> str:
    return reduce(__add__, map(_clean_char(keep, ignore, message), s))


def _clean_hex_string(s: str, ignore: str = "_") -> str:
    return _clean_string(s, keep=__HEX_DIGITS, ignore=ignore, message="hexadecimal string")


def _clean_bit_string(s: str, ignore: str = "_") -> str:
    return _clean_string(s, keep=__BIT_DIGITS, ignore=ignore, message="bit string")


def _align_string(left, right):
    match len(left)-len(right):
        case l if l < 0:
            # left is shorter
            return left.lpad(len(right)), right
        case l if l == 0:
            # both are same length
            return left, right
        case l if l > 0:
            # left is longer
            return left, right.lpad(len(left))


def _bitwise_operation(left, right, op):
    match left, right:
        case ByteString(), ByteString():
            fmt = '02X'
        case HexString(), HexString():
            fmt = 'X'
        case BitString(), BitString():
            fmt = 'X'

    return ''.join(([format(op(int(l), int(r)), fmt) for l, r in zip(*_align_string(left, right))]))


# 'BitString' class
class BitString(UserString):
    def __init__(self, value: int | Sequence, *, ignore: str = "_"):
        if isinstance(value, int):
            value_string = format(value, "b")
        elif isinstance(value, str):
            value_string = _clean_bit_string(value, ignore)
        elif isinstance(value, bytes):
            value_string = ''.join([format(b, '08b') for b in value])
        elif isinstance(value, list):
            value_string = ''.join([format(b, '08b') for b in value])
        else:
            raise TypeError(
                F"BitString()| unsupported initializer type: {type(value)}")

        super().__init__(value_string)

    def __int__(self) -> int:
        return int(self.data, 2)

    def __repr__(self):
        return F"BitString('{self}')"

    def __hash__(self):
        return hash(self.data)

    def __eq__(self, string: SupportsInt):
        return int(self) == int(string)

    def __lt__(self, string: SupportsInt):
        return int(self) < int(string)

    def __le__(self, string: SupportsInt):
        return int(self) <= int(string)

    def __gt__(self, string: SupportsInt):
        return int(self) > int(string)

    def __ge__(self, string: SupportsInt):
        return int(self) >= int(string)

    def __or__(self, other: BitString) -> BitString:
        return BitString(_bitwise_operation(self, other, __or__))

    def __xor__(self, other: BitString) -> BitString:
        return BitString(_bitwise_operation(self, other, __xor__))

    def __and__(self, other: BitString) -> BitString:
        return BitString(_bitwise_operation(self, other, __and__))

    def __invert__(self) -> BitString:
        return self ^ BitString('1' * len(self))

    def lpad(self, size: int) -> BitString:
        if len(self) < size:
            return BitString('0' * (size-len(self))) + self
        else:
            return self

    def rpad(self, size: int) -> BitString:
        if len(self) < size:
            return self + BitString('0' * (size-len(self)))
        else:
            return self

    def blocks(self, blocksize: int) -> Iterable[BitString]:
        nr_blocks = math.ceil(len(self) / blocksize)
        return (self[i*blocksize:(i+1)*blocksize] for i in range(nr_blocks))

    # def join(self, seq: Iterable[BitString]) -> BitString:
    #     return reduce(__add__, seq)

    def permute(self, permutation: list[int]) -> BitString:
        str_out: str = ''

        for i in permutation:
            str_out += str(self[i-1])

        return BitString(str_out)

    def expand(self, expansion: list[int]) -> BitString:
        return self.permute(expansion)

    def left_circular_shit(self, shift: int) -> BitString:
        return self[shift:] + self[:shift]

    @property
    def byte_string(self) -> ByteString:
        if len(self) % 8 == 0:
            return ByteString([int(b) for b in self.blocks(8)])
        else:
            return ByteString([int(b) for b in self.zfill(len(self)+8 - len(self) % 8).blocks(8)])


# 'HexString' class
class HexString(UserString):
    def __init__(self, value: int | Sequence, *, ignore: str = "_"):
        if isinstance(value, int):
            value_string = format(value, "X")
        elif isinstance(value, str):
            value_string = _clean_hex_string(value, ignore)
        elif isinstance(value, bytes):
            value_string = ''.join([format(b, '02X') for b in value])
        elif isinstance(value, list):
            value_string = ''.join([format(b, '02X') for b in value])
        else:
            raise TypeError(
                F"HexString()| unsupported initializer type: {type(value)}")

        super().__init__(value_string)

    def __int__(self) -> int:
        return int(self.data, 16)

    def __str__(self):
        return str(self.data.upper())

    def __repr__(self):
        return F"HexString('{self}')"

    def __hash__(self):
        return hash(self.data.upper())

    def __eq__(self, string: SupportsInt):
        return int(self) == int(string)

    def __lt__(self, string: SupportsInt):
        return int(self) < int(string)

    def __le__(self, string: SupportsInt):
        return int(self) <= int(string)

    def __gt__(self, string: SupportsInt):
        return int(self) > int(string)

    def __ge__(self, string: SupportsInt):
        return int(self) >= int(string)

    def __or__(self, other: HexString) -> HexString:
        return HexString(_bitwise_operation(self, other, __or__))

    def __xor__(self, other: HexString) -> HexString:
        return HexString(_bitwise_operation(self, other, __xor__))

    def __and__(self, other: HexString) -> HexString:
        return HexString(_bitwise_operation(self, other, __and__))

    def __invert__(self) -> HexString:
        return self ^ HexString('F' * len(self))

    def lpad(self, size: int) -> HexString:
        if len(self) < size:
            return HexString('0' * (size-len(self))) + self
        else:
            return self

    def rpad(self, size: int) -> HexString:
        if len(self) < size:
            return self + HexString('0' * (size-len(self)))
        else:
            return self

    # @property
    # def bit_length(self) -> int:
    #     return len(self) * 4

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

    def blocks(self, blocksize: int) -> Iterable[HexString]:
        nr_blocks = math.ceil(len(self) / blocksize)
        return (self[i*2*blocksize:(i+1)*2*blocksize] for i in range(nr_blocks))

    # def join(self, seq: Iterable[HexString]) -> HexString:
    #     return reduce(__add__, seq)

    @property
    def bytestring(self) -> ByteString:
        if len(self) % 2 == 0:
            return ByteString(str(self))
        else:
            return ByteString('0' + str(self))


# 'ByteString' class
class ByteString(HexString):
    def __init__(self, value: int | Sequence, *, ignore: str = "_"):
        if isinstance(value, int):
            value_string = format(value, "X")
            if len(value_string) % 2 != 0:
                value_string = '0' + value_string
        elif isinstance(value, str):
            value_string = _clean_hex_string(value, ignore)
            if len(value_string) % 2 != 0:
                raise ValueError(
                    F"ByteString()| received off number of nibbles: {value_string}")
        elif isinstance(value, bytes):
            value_string = ''.join([format(b, '02X') for b in value])
        elif isinstance(value, list):
            value_string = ''.join([format(int(b), '02X') for b in value])
        else:
            raise TypeError(
                F"ByteString()| unsupported initializer type: {type(value)}")

        super().__init__(value_string)

    def __int__(self) -> int:
        return int(self.data, 16)

    def __str__(self):
        return str(self.data.upper())

    def __repr__(self):
        return F"ByteString('{self.data.upper()}')"

    def __getitem__(self, key) -> ByteString:
        return ByteString(self.bytes[key])

    def __len__(self) -> int:
        return len(self.bytes)

    def __hash__(self):
        return hash(self.data.upper())

    def __eq__(self, string: SupportsInt):
        if isinstance(string, str):
            return int(self) == int(string, 16)
        else:
            return int(self) == int(string)

    def __lt__(self, string: SupportsInt):
        return int(self) < int(string)

    def __le__(self, string: SupportsInt):
        return int(self) <= int(string)

    def __gt__(self, string: SupportsInt):
        return int(self) > int(string)

    def __ge__(self, string: SupportsInt):
        return int(self) >= int(string)

    def __or__(self, other: ByteString) -> ByteString:
        return ByteString(_bitwise_operation(self, other, __or__))

    def __xor__(self, other: ByteString) -> ByteString:
        return ByteString(_bitwise_operation(self, other, __xor__))

    def __and__(self, other: ByteString) -> ByteString:
        return ByteString(_bitwise_operation(self, other, __and__))

    def __invert__(self) -> ByteString:
        return self ^ ByteString('FF' * len(self))

    @property
    def bytes(self) -> bytes:
        return bytes.fromhex(self.data)

    @property
    def list(self):
        return [int(b) for b in self.bytes]

    @property
    def array(self):
        return array('B', self.bytes)

    @property
    def bit_string(self) -> BitString:
        return BitString(self.bytes)

    def blocks(self, blocksize: int) -> Iterable[ByteString]:
        nr_blocks = math.ceil(len(self) / blocksize)
        return (self[i*blocksize:(i+1)*blocksize] for i in range(nr_blocks))

    def lpad(self, size: int) -> ByteString:
        return self.zfill(2*size)

    def rpad(self, size: int) -> ByteString:
        if len(self) < size:
            return self + ByteString('00' * (size-len(self)))
        else:
            return self

    def mask(self, mask: int) -> ByteString:
        return self & ByteString(mask)

    def is_bit_set(self, bit: int) -> bool:
        return self.mask(1 << (bit-1)) == 1 << (bit-1)

    def is_bit_unset(self, bit: int) -> bool:
        return not self.is_bit_set(bit)

    # def __rshift__(self, shift: int) -> ByteString:
    #     return ByteString.from_int(self.int >> shift).lpad(len(self))

    def startswith(self, prefix, start=0, end=_sys.maxsize):
        if isinstance(prefix, str):
            return self.data.upper().startswith(prefix.upper(), start, end)
        else:
            return self.data.upper().startswith(map(upper, prefix), start, end)
