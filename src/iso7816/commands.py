"""commands.py
"""

# Standard library imports
from enum import IntEnum

# Third party imports

# Local application imports
from common.hstr import clean as _clean
from iso7816.apdu import CommandField, CommandApdu, _dict_to_string, _byte_to_string
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
        apdu_str = _dict_to_string({CommandField.Class: CLA.str(), CommandField.Instruction: 'C0',
                                    CommandField.P1: '00', CommandField.P2: '00', CommandField.Le: _byte_to_string(Le)})
        super().__init__(apdu_str)


def GET_RESPONSE(CLA: CLA, Le: int) -> GetResponse:
    return GetResponse(CLA, Le)


class Select(CommandApdu):
    def __init__(self, secure_messaging: SecureMessaging, chaining: Chaining, logical_channel: int, selection: Selection, file_occurrence: FileOccurrence, fci: FileControlInformation, data: str = None, Le: str = None):
        apdu_dict = {CommandField.Class: CLA(secure_messaging, chaining, logical_channel).str(),
                     CommandField.Instruction: 'A4'}

        apdu_dict[CommandField.P1] = F"{selection:02x}"
        apdu_dict[CommandField.P2] = F"{file_occurrence + fci:02X}"

        if data is not None:
            apdu_dict[CommandField.Data] = _clean(data, 'SELECT()', 'data')

        if Le is not None:
            apdu_dict[CommandField.Le] = _clean(Le, 'SELECT()', 'Le')

        super.__init__(_dict_to_string(apdu_dict))


def SELECT(secure_messaging: SecureMessaging, chaining: Chaining, logical_channel: int, selection: Selection, file_occurrence: FileOccurrence, fci: FileControlInformation, data: str = None, Le: str = None) -> CommandApdu:
    return Select(secure_messaging, chaining, logical_channel, selection, file_occurrence, fci, data, Le)
