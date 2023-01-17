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


def SELECT(aid: Union[str, ApplicationIdentifier]) -> CommandApdu:
    """SELECT(): generate CommandApdu for SELECT command
    """
    apdu = {CommandField.Header: '00A40400', CommandField.Le: '00'}

    if aid in ApplicationIdentifier:
        apdu[CommandField.Data] = aid.value
    else:
        apdu[CommandField.Data] = _clean(aid, "emv.SELECT()", 'aid')

    return CommandApdu.from_dict(apdu)


def GET_PROCESSING_OPTIONS(pdol: str = '') -> CommandApdu:
    """GET_PROCESSING_OPTIONS(): generate APDU for GET PROCESSING OPTIONS command
    """
    apdu = {CommandField.Header: '80A80000',
            CommandField.Data: encode('83', pdol),
            CommandField.Le: '00'}

    return CommandApdu.from_dict(apdu)


def GPO(pdol: str) -> CommandApdu:
    """GPO(): generate APDU for GET PROCESSING OPTIONS command
    """
    return GET_PROCESSING_OPTIONS(pdol)


def READ_RECORD(SFI: int, record: int) -> CommandApdu:
    """READ_RECORD(): generate APDU for READ RECORD command
    """
    apdu = {CommandField.Class: '00',
            CommandField.Instruction: 'B2',
            CommandField.P1: F"{record:02X}",
            CommandField.P2: F"{SFI*8+4:02X}",
            CommandField.Le: '00'}

    return CommandApdu.from_dict(apdu)


def GET_DATA(tag: Union[str, GetDataObject]) -> CommandApdu:
    """GET_DATA: generate APDU for GET DATA command
    """
    apdu = {CommandField.Class: '80',
            CommandField.Instruction: 'CA',
            CommandField.Le: '00'}

    if tag in GetDataObject:
        apdu[CommandField.P1] = tag.value[0:2]
        apdu[CommandField.P2] = tag.value[2:4]
    else:
        apdu[CommandField.P1] = _clean(tag[0:2])
        apdu[CommandField.P2] = _clean(tag[2:4])

    return CommandApdu.from_dict(apdu)
