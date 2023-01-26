"""gp.py
"""

# Standard library imports
from typing import Union

# Third party imports

# Local application imports
from pcsc.scard import Protocol, send_apdu
from globalplatform import SELECT as _SELECT, GET_DATA as _GET_DATA, FileOccurrence, ApplicationIdentifier, SecureMessaging, GetDataObject


def SELECT(hcard, protocol: Protocol, logical_channel: int, file_occurrence: FileOccurrence, application_identifier: ApplicationIdentifier):
    return send_apdu(hcard, protocol, _SELECT(logical_channel, file_occurrence, application_identifier))


def GET_DATA(hcard, protocol: Protocol, secure_messaging: SecureMessaging, logical_channel: int, tag: Union[str, GetDataObject]):
    return send_apdu(hcard, protocol, _GET_DATA(secure_messaging, logical_channel, tag))


def GET_CPLC(hcard, protocol: Protocol, secure_messaging: SecureMessaging, logical_channel: int):
    return send_apdu(hcard, protocol, _GET_DATA(secure_messaging, logical_channel, GetDataObject.CardProductionLifeCycle))
