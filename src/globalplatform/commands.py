"""commands.py
"""

# Standard library imports
from enum import Enum, IntEnum
from typing import Union

# Third party imports

# Local application imports
from common.hstr import clean as _clean, to_intlist as _to_intlist
from globalplatform.encodings import SecureMessaging, CLA as GP_CLA
from iso7816 import CommandApdu, CommandField, CLA as ISO_CLA, Chaining, SecureMessaging as ISO_SecureMessaging


# Enum Definitions
class GetDataObject(Enum):
    ListOfApplications = '2F00'
    IssuerIdentificationNumber = '0042'
    CardImageNumber = '0045'
    CardData = '0066'
    KeyInformationTemplate = '00E0'
    CardCapabilityInformation = '0067'
    CurrentSecurityLevel = '00D3'
    SecurityDomainManagerURL = '5F50'
    ConfirmationCounter = '00C2'
    SequenceCounterOfTheDefaultKeyVersionNumber = '00C1'
    CardProductionLifeCycle = '9F7F'


class FileOccurrence(IntEnum):
    FirstOrOnlyOccurrence = 0x0
    NextOccurrence = 0x2


class ApplicationIdentifier(Enum):
    GlobalPlatformSecurityDomain = 'A000000151000000'
    Default = ''


# Command APDUs defined by GP
class GetData(CommandApdu):
    def __init__(self, secure_messaging: SecureMessaging, logical_channel: int, tag: Union[str, GetDataObject]):
        if isinstance(tag, GetDataObject):
            P1 = int(tag.value[0:2], 16)
            P2 = int(tag.value[2:4], 16)
        elif isinstance(tag, str):
            P1 = int(_clean(tag[0:2]), 16)
            P2 = int(_clean(tag[2:4]), 16)
        else:
            raise TypeError(
                F"globalplatform.GetData(): tag should be of type str or GetDataObject, received: {type(tag)}")

        super().__init__(GP_CLA(secure_messaging, logical_channel).value, 0xCA, P1, P2, Le=0x100)


def GET_DATA(secure_messaging: SecureMessaging, logical_channel: int, tag: Union[str, GetDataObject]) -> GetData:
    """GET_DATA: generate APDU for GET DATA command
    """
    return GetData(secure_messaging, logical_channel, tag)


class Select(CommandApdu):
    def __init__(self, logical_channel: int, file_occurrence: FileOccurrence, application_identifier: Union[str, ApplicationIdentifier]):
        cla = ISO_CLA(ISO_SecureMessaging.No,
                      Chaining.LastOrOnly, logical_channel).value
        ins = 0xA4
        p1 = 0x04
        p2 = file_occurrence.value
        Le = 0x100

        if isinstance(application_identifier, ApplicationIdentifier):
            if application_identifier == ApplicationIdentifier.Default:
                super().__init__(cla, ins, p1, p2, Le=Le)
            else:
                data = _to_intlist(application_identifier.value)
                super().__init__(cla, ins, p1, p2, data=data, Le=Le)

        elif isinstance(application_identifier, str):
            data = _to_intlist(application_identifier,
                               'SELECT()', 'application_identifier')
            super().__init__(cla, ins, p1, p2, data=data, Le=Le)

        else:
            raise TypeError(
                F"globalplatform.Select(): application_identifier should be of type str or ApplicationIdentifier, received: {type(application_identifier)}")


def SELECT(logical_channel: int, file_occurrence: FileOccurrence, application_identifier: Union[str, ApplicationIdentifier]) -> Select:
    return Select(logical_channel, file_occurrence, application_identifier)
