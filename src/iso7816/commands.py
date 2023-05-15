"""commands.py
"""

# Standard library imports
from enum import IntEnum

# Third party imports

# Local application imports
from common.hstr import clean as _clean
from iso7816.apdu import CommandApdu
from iso7816.encodings import SecureMessaging, Chaining, CLA


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
    def __init__(self, CLA: CLA, Le: int):
        super().__init__(CLA.value, 0xC0, 0x00, 0x00, Le=Le)


def GET_RESPONSE(CLA: CLA, Le: int) -> GetResponse:
    return GetResponse(CLA, Le)


class Select(CommandApdu):
    def __init__(self,
                 secure_messaging: SecureMessaging,
                 chaining: Chaining,
                 logical_channel: int,
                 selection: Selection,
                 file_occurrence: FileOccurrence,
                 fci: FileControlInformation,
                 data: list[int] = None,
                 Le: int = None):
        cla: int = CLA(secure_messaging, chaining, logical_channel).value
        INS: int = 0xA4
        P1: int = selection.value
        P2: int = file_occurrence.value + fci.value

        super().__init__(cla, INS, P1, P2, data=data, Le=Le)


def SELECT(secure_messaging: SecureMessaging,
           chaining: Chaining,
           logical_channel: int,
           selection: Selection,
           file_occurrence: FileOccurrence,
           fci: FileControlInformation,
           data: list[int] = None,
           Le: int = None) -> Select:
    return Select(secure_messaging, chaining, logical_channel, selection, file_occurrence, fci, data, Le)
