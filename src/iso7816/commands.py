"""commands.py
"""

# Standard library imports
from typing import Optional

# Third party imports

# Local application imports
from common.binary import ByteString
from .apdu import CommandApdu
from .encodings import CLA, Selection, FileOccurrence, FileControlInformation


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
