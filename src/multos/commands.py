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


def GET_MULTOS_DATA() -> CommandApdu:
    """GET_MULTOS_DATA: generate APDU for GET MULTOS DATA command
    """
    return CommandApdu('800000007F')
