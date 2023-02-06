"""gp.py
"""

# Standard library imports
from typing import Union

# Third party imports

# Local application imports
from common.ber import parse_to_dict
from globalplatform import SELECT as _SELECT, GET_DATA as _GET_DATA, FileOccurrence, ApplicationIdentifier, SecureMessaging, GetDataObject, CPLC, CardPersonalizationLifeCycleData
from pcsc.card import Protocol, send_apdu


def SELECT(hcard, protocol: Protocol, logical_channel: int = 0, file_occurrence: FileOccurrence = FileOccurrence.FirstOrOnlyOccurrence, application_identifier: ApplicationIdentifier = ApplicationIdentifier.Default):
    return send_apdu(hcard, protocol, _SELECT(logical_channel, file_occurrence, application_identifier))


def GET_DATA(hcard, protocol: Protocol, tag: Union[str, GetDataObject], secure_messaging: SecureMessaging = SecureMessaging.No, logical_channel: int = 0):
    return send_apdu(hcard, protocol, _GET_DATA(secure_messaging, logical_channel, tag))


def GET_CPLC(hcard, protocol: Protocol, secure_messaging: SecureMessaging = SecureMessaging.No, logical_channel: int = 0):
    r, error = send_apdu(hcard, protocol, _GET_DATA(secure_messaging,
                                                    logical_channel,
                                                    GetDataObject.CardProductionLifeCycle))

    if error is not None:
        return None, error
    elif r.SW12() != '9000':
        return None, F"Response bytes to GET [CPLC] DATA is not 9000 (SW12 = {r.SW12()})"
    else:
        cplc_data = CPLC(parse_to_dict(r.data()).get('9F7F', {}))
        return cplc_data, None
