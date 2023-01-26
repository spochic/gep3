"""commands.py
"""

# Standard library imports
from enum import Enum, IntEnum
from typing import Union

# Third party imports

# Local application imports
from common.hstr import clean as _clean
from globalplatform.encodings import SecureMessaging, CLA as GP_CLA
from iso7816 import CommandApdu, CommandField, CLA as ISO_CLA, Chaining


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


def GET_DATA(secure_messaging: SecureMessaging, logical_channel: int, tag: Union[str, GetDataObject]) -> CommandApdu:
    """GET_DATA: generate APDU for GET DATA command
    """
    apdu = {CommandField.Class: GP_CLA(secure_messaging, logical_channel).str(),
            CommandField.Instruction: 'CA',
            CommandField.Le: '00'}

    if tag in GetDataObject:
        apdu[CommandField.P1] = tag.value[0:2]
        apdu[CommandField.P2] = tag.value[2:4]
    else:
        apdu[CommandField.P1] = _clean(tag[0:2])
        apdu[CommandField.P2] = _clean(tag[2:4])

    return CommandApdu.from_dict(apdu)


def SELECT(logical_channel: int, file_occurrence: FileOccurrence, application_identifier: Union[str, ApplicationIdentifier]) -> CommandApdu:
    apdu_dict = {CommandField.Class: ISO_CLA(SecureMessaging.No, Chaining.LastOrOnly, logical_channel).str(),
                 CommandField.Instruction: 'A4',
                 CommandField.P1: '04',
                 CommandField.P2: F"{file_occurrence:02X}",
                 CommandField.Le: '00'}

    if application_identifier in ApplicationIdentifier:
        if application_identifier != ApplicationIdentifier.Default:
            apdu_dict[CommandField.Data] = application_identifier.value
    else:
        apdu_dict[CommandField.Data] = _clean(
            application_identifier, 'SELECT()', 'application_identifier')

    return CommandApdu.from_dict(apdu_dict)
