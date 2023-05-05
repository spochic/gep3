"""gp.py
"""

# Standard library imports
from typing import Union

# Third party imports

# Local application imports
from .ifd import InterfaceDevice
from .apdu_exchange import send_apdu
from ccid import Protocol
from iso7816 import ResponseApdu
from globalplatform import FileOccurrence, ApplicationIdentifier, Select, GetData, SecureMessaging, GetDataObject, CPLC


def select(ifd: InterfaceDevice,
           protocol: Protocol,
           logical_channel: int = 0,
           file_occurrence: FileOccurrence = FileOccurrence.FirstOrOnlyOccurrence,
           application_identifier: ApplicationIdentifier = ApplicationIdentifier.Default,
           timeout=None) -> ResponseApdu:
    return send_apdu(ifd, protocol, Select(logical_channel, file_occurrence, application_identifier), timeout)


def get_data(ifd: InterfaceDevice,
             protocol: Protocol,
             tag: Union[str, GetDataObject],
             secure_messaging: SecureMessaging = SecureMessaging.No,
             logical_channel: int = 0,
             timeout=None) -> ResponseApdu:
    return send_apdu(ifd, protocol, GetData(secure_messaging, logical_channel, tag), timeout)


def get_cplc(ifd: InterfaceDevice,
             protocol: Protocol,
             secure_messaging: SecureMessaging = SecureMessaging.No,
             logical_channel: int = 0,
             timeout=None) -> Union[None, CPLC]:
    response_apdu: ResponseApdu = get_data(
        ifd, protocol, GetDataObject.CardProductionLifeCycle, secure_messaging, logical_channel, timeout)
    if response_apdu.SW12() == '9000':
        return CPLC(response_apdu.data()[6:])
    else:
        None
