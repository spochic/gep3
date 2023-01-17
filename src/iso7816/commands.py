"""commands.py
"""

# Standard library imports
from enum import IntEnum

# Third party imports

# Local application imports
from common.hstr import clean as _clean
from iso7816.apdu import CommandField, CommandApdu
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


def GET_RESPONSE(CLA: str, Le: str):
    return CommandApdu.from_dict({CommandField.Class: CLA, CommandField.Instruction: 'C0', CommandField.P1: '00', CommandField.P2: '00', CommandField.Le: Le})


def SELECT(secure_messaging: SecureMessaging, chaining: Chaining, logical_channel: int, selection: Selection, file_occurrence: FileOccurrence, fci: FileControlInformation, data: str = None, Le: str = None) -> CommandApdu:
    apdu_dict = {CommandField.Class: CLA(secure_messaging, chaining, logical_channel).str(),
                 CommandField.Instruction: 'A4'}

    apdu_dict[CommandField.P1] = F"{selection:02x}"
    apdu_dict[CommandField.P2] = F"{file_occurrence + fci:02X}"

    if data is not None:
        apdu_dict[CommandField.Data] = _clean(data, 'SELECT()', 'data')

    if Le is not None:
        apdu_dict[CommandField.Le] = _clean(Le, 'SELECT()', 'Le')

    return CommandApdu.from_dict(apdu_dict)
