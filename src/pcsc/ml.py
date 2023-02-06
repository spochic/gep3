"""ml.py
"""

# Standard library imports
from typing import Union

# Third party imports

# Local application imports
from multos import GET_MULTOS_DATA as _GET_MULTOS_DATA, MultosData
from pcsc.card import Protocol, send_apdu


def GET_MULTOS_DATA(hcard, protocol: Protocol) -> MultosData:
    r, error = send_apdu(hcard, protocol, _GET_MULTOS_DATA())

    if error is not None:
        return None, error
    elif r.SW12() != '9000':
        return None, F"Response bytes to GET MULTOS DATA is not 9000 (SW12 = {r.SW12()})"
    else:
        multos_data = MultosData(r.data())
        return multos_data, None
