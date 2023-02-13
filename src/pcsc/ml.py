"""ml.py
"""

# Standard library imports

# Third party imports

# Local application imports
from multos import GET_MULTOS_DATA as _GET_MULTOS_DATA, MultosData, MultosDataField
from pcsc.card import Protocol, send_apdu


def GET_MULTOS_DATA(hcard, protocol: Protocol) -> MultosData:
    r, error = send_apdu(hcard, protocol, _GET_MULTOS_DATA())

    if error is not None:
        return None, F"Error getting the MULTOS data ({error})"

    elif (sw12 := r.SW12()) != '9000':
        return None, F"Error getting the MULTOS data (SW12 = {sw12})"

    else:
        multos_data = MultosData(r.data())
        return multos_data, None
