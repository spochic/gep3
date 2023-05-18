"""emv.py
"""

# Standard library imports
from typing import Union

# Third party imports

# Local application imports
from pyusbccid.ifd import InterfaceDevice
from pyusbccid.apdu_exchange import send_apdu
from ccid import Protocol
from iso7816 import ResponseApdu
from emv import Select, ApplicationIdentifier, GetProcessingOptions


def SELECT(ifd: InterfaceDevice,
           protocol: Protocol,
           aid: Union[str, ApplicationIdentifier],
           timeout=None) -> ResponseApdu:
    return send_apdu(ifd, protocol, Select(aid), timeout)


#
# /|\ TODO: CREATE TLV, DOOL, etc, classes in common.ber, emv, ...
#
def GPO(ifd: InterfaceDevice,
        protocol: Protocol,
        pdol: str = '',
        timeout=None) -> ResponseApdu:
    return send_apdu(ifd, protocol, GetProcessingOptions(pdol), timeout)


# def READ_RECORD(card_service: card._CardService, sfi: int, record: int, trace=None):
#     return card.send_apdu(card_service, command.READ_RECORD(sfi, record), trace=trace)


# def READ_RECORDs(card_service: card._CardService, AFL: str, trace=None):
#     output = []

#     r, err = records.decode_afl(AFL)
#     if err is not None:
#         return []
#     else:
#         for (sfi, first, last, _) in r:
#             for n in range(first, last+1):
#                 r, err = READ_RECORD(card_service, sfi, n, trace=trace)
#                 output.append((r, err))
#                 if err != '':
#                     return output
#         return output


# def GET_DATA(card_service: card._CardService, tag: str, trace=None):
#     return card.send_apdu(card_service, command.GET_DATA(tag), trace=trace)
