"""commands.py
"""

# Standard library imports
from enum import IntEnum
from typing import Optional

# Third party imports

# Local application imports
from common.binary import ByteString
from .apdu import CommandApdu
from .encodings import CLA


# Enum Definitions
class Selection(IntEnum):
    SelectMForDForEF = 0x00
    SelectChildDF = 0x01
    SelectEFUnderCurrentDF = 0x02
    SelectParentDFOfCurrentDF = 0x03
    SelectByDFName = 0x04
    SelectFromMF = 0x08
    SelectFromCurrentDF = 0x09


class FileOccurrence(IntEnum):
    FirstOrOnlyOccurrence = 0x0
    LastOccurrence = 0x1
    NextOccurrence = 0x2
    PreviousOccurrence = 0x3


class FileControlInformation(IntEnum):
    ReturnFCITemplate = 0x00
    ReturnFCPTempalte = 0x10
    ReturnFMDTemplate = 0x20
    NoResponseOrProprietary = 0x30


#
# Commands for interchange
#
class GetResponse(CommandApdu):
    def __init__(self, class_byte: ByteString, Ne: int):
        header = (CLA(class_byte) + ByteString('C00000')).blocks(1)
        super().__init__(*header, data_field=None, Ne=Ne)


GET_RESPONSE = GetResponse


class Select(CommandApdu):
    def __init__(self,
                 class_byte: ByteString,
                 P1: ByteString,
                 P2: ByteString,
                 data_field: Optional[ByteString],
                 Ne: Optional[int]):
        if len(P1) != 1:
            raise ValueError(F"P1 should be 1 byte, received: {P1}")
        if len(P2) != 1:
            raise ValueError(F"P2 should be 1 byte, received: {P2}")

        header = (CLA(class_byte) + ByteString('A4') + P1 + P2).blocks(1)

        super().__init__(*header, data_field=data_field, Ne=Ne)


def SELECT(class_byte: ByteString,
           selection: Selection,
           file_occurrence: FileOccurrence,
           fci: FileControlInformation,
           data_field: Optional[ByteString],
           Ne: Optional[int]) -> Select:
    P1 = ByteString(F"{selection.value:02X}")
    P2 = ByteString(F"{file_occurrence.value + fci.value:02X}")

    return Select(class_byte, P1, P2, data_field, Ne)
