"""commands.py
"""

# Standard library imports
from enum import StrEnum

# Third party imports

# Local application imports
# from common.ber import encode
from common.binary import ByteString
from iso7816.apdu import CommandApdu, CommandField, create_command_APDU


# Enum Definitions
class ApplicationIdentifier(StrEnum):
    Mastercard = 'A0000000041010'
    Visa = 'A0000000031010'
    Maestro = 'A00000000410103060'
    EVC = 'A0000008864040'
    EVC_test = 'A0000008863030'
    Dummy = 'A0000008862020'
    Dummy_test = 'A0000008861010'


class GetDataObject(StrEnum):
    ATC = '9F36'
    LastOnlineATCRegister = '9F13'
    PINTryCounter = '9F17'
    LogFormat = '9F4F'


# Command APDUs defined by EMV
class Select(CommandApdu):
    def __init__(self, aid: ByteString):
        super().__init__(ByteString(
            F'00A40400{len(aid):02X}') + aid + ByteString('00'))


def SELECT(aid: ByteString | ApplicationIdentifier) -> Select:
    """SELECT(): generate CommandApdu for SELECT command
    """
    if isinstance(aid, ApplicationIdentifier):
        return Select(ByteString(aid.value))
    elif isinstance(aid, ByteString):
        return Select(aid)
    else:
        raise TypeError(
            F"emv.SELECT(): aid should be of type ByteString or ApplicationIdentifier, received: {type(aid)}")


class GetProcessingOptions(CommandApdu):
    def __init__(self, pdol: ByteString):
        super().__init__(ByteString(
            F'80A80000{len(pdol):02X}') + pdol + ByteString('00'))


def GET_PROCESSING_OPTIONS(pdol: ByteString | None) -> GetProcessingOptions:
    """GET_PROCESSING_OPTIONS(): generate APDU for GET PROCESSING OPTIONS command
    """
    if pdol:
        return GetProcessingOptions(pdol)
    else:
        return GetProcessingOptions(ByteString('8300'))


GPO = GET_PROCESSING_OPTIONS


class ReadRecord(CommandApdu):
    def __init__(self, SFI: int, record: int):
        super().__init__(ByteString(F"00B2{record:02X}{SFI*8+4}00"))


def READ_RECORD(SFI: int, record: int) -> ReadRecord:
    """READ_RECORD(): generate APDU for READ RECORD command
    """
    return ReadRecord(SFI, record)


class GetData(CommandApdu):
    def __init__(self, tag: ByteString):
        super().__init__(ByteString(F'80CA{tag}00'))


def GET_DATA(tag: ByteString | GetDataObject) -> GetData:
    """GET_DATA: generate APDU for GET DATA command
    """
    if isinstance(tag, GetDataObject):
        if len(tag.value) == 2:
            P1 = ByteString('00')
            P2 = ByteString(tag.value)
        else:
            P1 = ByteString(tag.value[0:2])
            P2 = ByteString(tag.value[2:4])

    elif isinstance(tag, ByteString):
        P1 = tag[0:2]
        P2 = tag[2:4]

    else:
        raise TypeError(
            F"emv.GET_DATA(): tag should be of type ByteString or GetDataObject, received: {type(tag)}")

    return GetData(P1+P2)
