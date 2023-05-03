"""commands.py
"""

# Standard library imports
from enum import Enum
from typing import Union

# Third party imports

# Local application imports
from common.ber import encode
from common.hstr import clean as _clean
from iso7816.apdu import CommandApdu, CommandField
from iso7816.commands import _dict_to_string


# Enum Definitions
class ApplicationIdentifier(Enum):
    Mastercard = 'A0000000041010'
    Visa = 'A0000000031010'
    Maestro = 'A00000000410103060'
    EVC = 'A0000008864040'
    EVC_test = 'A0000008863030'
    Dummy = 'A0000008862020'
    Dummy_test = 'A0000008861010'


class GetDataObject(Enum):
    ATC = '9F36'
    LastOnlineATCRegister = '9F13'
    PINTryCounter = '9F17'
    LogFormat = '9F4f'


# Command APDUs defined by EMV
class Select(CommandApdu):
    def __init__(self, aid: Union[str, ApplicationIdentifier]):
        apdu_dict = {CommandField.Header: '00A40400', CommandField.Le: '00'}

        if aid in ApplicationIdentifier:
            apdu_dict[CommandField.Data] = aid.value
        else:
            apdu_dict[CommandField.Data] = _clean(aid, "emv.SELECT()", 'aid')

        super().__init__(_dict_to_string(apdu_dict))


def SELECT(aid: Union[str, ApplicationIdentifier]) -> Select:
    """SELECT(): generate CommandApdu for SELECT command
    """
    return Select(aid)


class GetProcessingOptions(CommandApdu):
    def __init__(self, pdol: str = ''):
        apdu_dict = {CommandField.Header: '80A80000',
                     CommandField.Data: encode('83', pdol),
                     CommandField.Le: '00'}

        super().__init__(_dict_to_string(apdu_dict))


def GET_PROCESSING_OPTIONS(pdol: str = '') -> GetProcessingOptions:
    """GET_PROCESSING_OPTIONS(): generate APDU for GET PROCESSING OPTIONS command
    """
    return GetProcessingOptions(pdol)


def GPO(pdol: str) -> GetProcessingOptions:
    """GPO(): generate APDU for GET PROCESSING OPTIONS command
    """
    return GET_PROCESSING_OPTIONS(pdol)


class ReadRecord(CommandApdu):
    def __init__(self, SFI: int, record: int):
        apdu_dict = {CommandField.Class: '00',
                     CommandField.Instruction: 'B2',
                     CommandField.P1: F"{record:02X}",
                     CommandField.P2: F"{SFI*8+4:02X}",
                     CommandField.Le: '00'}

        super().__init__(_dict_to_string(apdu_dict))


def READ_RECORD(SFI: int, record: int) -> ReadRecord:
    """READ_RECORD(): generate APDU for READ RECORD command
    """
    return ReadRecord(SFI, record)


class GetData(CommandApdu):
    def __init__(self, tag: Union[str, GetDataObject]):
        apdu_dict = {CommandField.Class: '80',
                     CommandField.Instruction: 'CA',
                     CommandField.Le: '00'}

        if tag in GetDataObject:
            apdu_dict[CommandField.P1] = tag.value[0:2]
            apdu_dict[CommandField.P2] = tag.value[2:4]
        else:
            apdu_dict[CommandField.P1] = _clean(tag[0:2])
            apdu_dict[CommandField.P2] = _clean(tag[2:4])

        super().__init__(_dict_to_string(apdu_dict))


def GET_DATA(tag: Union[str, GetDataObject]) -> GetData:
    """GET_DATA: generate APDU for GET DATA command
    """
    return GetData(tag)
