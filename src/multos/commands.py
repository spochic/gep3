"""commands.py
"""

# Standard library imports
from enum import Enum, IntEnum
from typing import Union

# Third party imports

# Local application imports
from common.hstr import clean as _clean
from multos.encodings import MultosData, MultosDataField
from iso7816 import CommandApdu, CommandField, CLA as ISO_CLA, Chaining


# Enum Definitions


# Command APDUs defined by MULTOS
class GetMultosData(CommandApdu):
    def __init__(self):
        super().__init__("800000007F")


def GET_MULTOS_DATA() -> GetMultosData:
    """GET_MULTOS_DATA: generate APDU for GET MULTOS DATA command
    """
    return GetMultosData()


class GetManufacturerData(CommandApdu):
    def __init__(self):
        super().__init__("8002000016")
