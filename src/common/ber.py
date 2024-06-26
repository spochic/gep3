"""ber.py
"""
# Standard library imports
from enum import IntEnum
from math import log2

# Third party imports


# Local application imports
from common.binary import HexString, ByteString
from common.parserc import null, byte, nibble, joint, one_of, exclude, generate, many, count


# Enum definitions
class TagClass(IntEnum):
    Universal = 0x00
    Application = 0x40
    ContextSpecific = 0x80
    Private = 0xC0


class TagConstruction(IntEnum):
    Primitive = 0x00
    Constructed = 0x20


#
# Class definitions
#
# Tag: tag identifier
class Tag(ByteString):
    def __init__(self, tag: str):
        super().__init__(tag)
        tag, remainder = T_fieldP.parse_partial(self.data)
        if remainder != '':
            raise ValueError(
                F"Unknown bytes '{remainder}' after tag '{tag}'")

        if len(self) == 1:
            if (tag_number := int(self) & 0x1F) == 0x1F:
                raise ValueError(
                    F"Tag(): 1-byte tag should not have b5-b1 = 11111, received: {self}")
            else:
                self.__tag_number = tag_number
                return

        if (int(self[0]) & 0x1F) != 0x1F:
            raise ValueError(
                F"Tag(): first byte of multi-byte tags should have b5-b1 = 11111, received: {self}")

        if len(self) > 2:
            if any(map(lambda n: (n & 0x80) == 0x00, self.list[1:-1])):
                raise ValueError(
                    F"Tag(): All but last tag byte should have b8 = 1, received: {self}")

        if (int(self[-1]) & 0x80) != 0x00:
            raise ValueError(
                F"Tag(): Last tag byte should have b8 = 0, received {self}")

        __subsequent_bytes = map(lambda n: n & 0x7F, self.list[2:])
        __tag_number = int(self[1]) & 0x7F
        for b in __subsequent_bytes:
            __tag_number = __tag_number << 7
            __tag_number += b

        self.__tag_number = __tag_number
        return

    @property
    def class_(self) -> TagClass:
        return TagClass(self.list[0] & 0xC0)

    @property
    def construction(self) -> TagConstruction:
        return TagConstruction(self.list[0] & 0x20)

    @property
    def number(self) -> int:
        return self.__tag_number


def create_tag(tag_class: TagClass, tag_construction: TagConstruction, tag_number: int) -> Tag:
    """create_tag(): create a Tag object based on individual fields
    """
    match tag_number:
        case number if number < 0:
            raise ValueError(
                F"create_tag(): Tag number should be positive, received: {tag_number}")

        case number if number < 31:
            tag = [tag_class+tag_construction+tag_number]

        case number if number < 128:
            tag = [tag_class+tag_construction+31, tag_number]

        case _:
            tag = [tag_class+tag_construction+31]

            subsequent_bytes = []
            while tag_number > 0:
                subsequent_bytes.append(128+(tag_number % 128))
                tag_number //= 128

            subsequent_bytes.reverse()
            subsequent_bytes[-1] &= 0x7F
            tag.extend(subsequent_bytes)

    return Tag(''.join([F"{b:02X}" for b in tag]))


# Length: length encoding
class Length(ByteString):
    def __init__(self, length: str):
        super().__init__(length)
        length, remainder = L_fieldP.parse_partial(self.data)
        if remainder != '':
            raise ValueError(
                F"Unknown bytes '{remainder}' after length '{length}'")

        length_bytes = self.bytes

        if len(length_bytes) == 1:
            if (length_bytes[0] & 0x80) == 0:
                self.__length = length_bytes[0]
            else:
                raise ValueError(
                    F"Single-byte length should have b8 = 0, received: {self}")
        elif len(length_bytes[1:]) == length_bytes[0] & 0x7F:
            self.__length = int.from_bytes(length_bytes[1:], byteorder='big')
        else:
            raise ValueError(
                F"Length should be {(length_bytes[0] & 0x7F) + 1} bytes, received: {self}")

    @property
    def value(self) -> int:
        return self.__length


def create_length(value: ByteString) -> Length:
    match len(value):
        case l if l < 128:
            return Length(F'{l:02X}')

        case l if log2(l) < 1017:
            nr_bits = len(value).bit_length()
            if nr_bits % 8 == 0:
                nr_bytes = nr_bits//8
            else:
                nr_bytes = nr_bits//8 + 1
            return Length(F"{128+nr_bytes:02X}" + format(len(value), F"0{nr_bytes*2}X"))

        case _:
            raise ValueError(F"Cannot encode length > 2^1016")


# TagLengthValue: TLV encoding
class TagLengthValue(ByteString):
    def __init__(self, tlv: str):
        super().__init__(tlv)
        partial_parse = TagLengthValueP.parse_partial(self.data)
        if partial_parse[1] != '':
            raise ValueError(
                F"Unknown bytes '{partial_parse[1]}' after TLV '{tlv}'")

        tag, length, value = partial_parse[0]
        self.__tag = Tag(tag)
        self.__length = Length(length)
        self.__value = ByteString(value)

    @property
    def tag(self) -> Tag:
        return self.__tag

    @property
    def length(self) -> Length:
        return self.__length

    @property
    def value(self) -> HexString:
        return self.__value


# class TagLength():
#     def __init__(self, tl: str):
#         pass


# class DataObjectList():
#     def __init__(self, dol: str):
#         pass


#
# Parser combinators
#
# Tag field parsers
__T_multi_byte_start = joint(one_of('13579bBdDfF'),
                             one_of('fF'))
__T_multi_byte_inner = joint(one_of('89aAbBcCdDeEfF'),
                             nibble)
__T_multi_byte_last = joint(one_of('01234567'),
                            nibble)
__T_single_byte = exclude(byte,
                          __T_multi_byte_start)


@generate
def __T_multi_byte():
    """Parses a multi-byte Tag Field.
    """
    start_tag = yield __T_multi_byte_start
    inner_tags = yield many(__T_multi_byte_inner)
    inner_tags = ''.join(inner_tags)
    last_tag = yield __T_multi_byte_last

    return start_tag + inner_tags + last_tag


T_fieldP = __T_single_byte | __T_multi_byte


# Length Field parser
__L_single_byte = joint(one_of('01234567'), nibble)
__L_multi_byte_start = joint(
    one_of('89aAbBcCdDeEfF'), nibble)


@generate
def __L_multi_byte():
    start_length = yield __L_multi_byte_start
    nr_bytes = int(start_length, 16) - 0x80
    subsequent_length = yield count(byte, nr_bytes)
    subsequent_length = ''.join(subsequent_length)

    return start_length + subsequent_length


L_fieldP = __L_single_byte | __L_multi_byte


# TLV parser
@generate
def TagLengthValueP():
    # ignore leading 00
    _ = yield many(null)

    tag = yield T_fieldP
    length = yield L_fieldP
    value = yield count(byte, Length(length).value)
    value = ''.join(value)

    # ignore trailing 00
    _ = yield many(null)

    return tag, length, value


# Old definitions
# def parse_to_dict(tlv_hstr: str):
#     pass


# def parse_dol(tlv_hstr: str):
#     pass

# def find(tag, tlv_object):
#     pass
