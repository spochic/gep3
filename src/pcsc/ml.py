"""ml.py
"""

# Standard library imports
from typing import Union

# Third party imports

# Local application imports
from common.ber import parse_to_dict
from multos import GET_MULTOS_DATA as _GET_MULTOS_DATA, MultosData, MultosDataField
from pcsc.scard import Protocol, send_apdu


def GET_MULTOS_DATA(hcard, protocol: Protocol) -> MultosData:
    r = send_apdu(hcard, protocol, _GET_MULTOS_DATA())
    multos_data = MultosData(r.data())

    return multos_data
