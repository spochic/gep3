"""gp.py
"""

# Standard library imports
from typing import Union

# Third party imports

# Local application imports
from common.ber import parse_to_dict
from globalplatform import SELECT as _SELECT, GET_DATA as _GET_DATA, FileOccurrence, ApplicationIdentifier, SecureMessaging, GetDataObject
from globalplatform.encodings import CPLC
from pcsc.scard import Protocol, send_apdu


def SELECT(hcard, protocol: Protocol, logical_channel: int, file_occurrence: FileOccurrence, application_identifier: ApplicationIdentifier):
    return send_apdu(hcard, protocol, _SELECT(logical_channel, file_occurrence, application_identifier))


def GET_DATA(hcard, protocol: Protocol, secure_messaging: SecureMessaging, logical_channel: int, tag: Union[str, GetDataObject]):
    return send_apdu(hcard, protocol, _GET_DATA(secure_messaging, logical_channel, tag))


def GET_CPLC(hcard, protocol: Protocol, secure_messaging: SecureMessaging, logical_channel: int):
    r = send_apdu(hcard, protocol, _GET_DATA(secure_messaging,
                  logical_channel, GetDataObject.CardProductionLifeCycle))

    cplc_data = CPLC(parse_to_dict(r.data()).get('9F7F', {}))

    return cplc_data
