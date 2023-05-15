"""commands.py
"""

# Standard library imports
from enum import Enum
from typing import Union

# Third party imports

# Local application imports
from common.ber import encode
from common.hstr import clean as _clean, to_intlist as _to_intlist
from iso7816.apdu import CommandApdu, CommandField


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
        if isinstance(aid, ApplicationIdentifier):
            data = _to_intlist(aid.value)
        elif isinstance(aid, str):
            data = _to_intlist(aid, "emv.SELECT()", 'aid')
        else:
            raise TypeError(
                F"emv.Select(): aid should be of type str or ApplicationIdentifier, received: {type(aid)}")

        super().__init__(0x00, 0xA4, 0x04, 0x00, data=data, Le=0x100)


def SELECT(aid: Union[str, ApplicationIdentifier]) -> Select:
    """SELECT(): generate CommandApdu for SELECT command
    """
    return Select(aid)


class GetProcessingOptions(CommandApdu):
    def __init__(self, pdol: str = ''):
        super().__init__(0x80, 0xA8, 0x00, 0x00,
                         data=_to_intlist(encode('83', pdol)), Le=0x100)


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
        super().__init__(0x00, 0xB2, record, SFI*8+4, Le=0x100)


def READ_RECORD(SFI: int, record: int) -> ReadRecord:
    """READ_RECORD(): generate APDU for READ RECORD command
    """
    return ReadRecord(SFI, record)


class GetData(CommandApdu):
    def __init__(self, tag: Union[str, GetDataObject]):
        if isinstance(tag, GetDataObject):
            P1 = int(tag.value[0:2], 16)
            P2 = int(tag.value[2:4], 16)

        elif isinstance(tag, str):
            P1 = int(tag[0:2], 16)
            P2 = int(tag[2:4], 16)

        else:
            raise TypeError(
                F"emv.GetData(): tag should be of type str or GetDataObject, received: {type(tag)}")

        super().__init__(0x80, 0xCA, P1, P2, Le=0x100)


def GET_DATA(tag: Union[str, GetDataObject]) -> GetData:
    """GET_DATA: generate APDU for GET DATA command
    """
    return GetData(tag)
