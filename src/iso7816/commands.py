"""iso7816.py
"""

# Standard library imports
from enum import Enum

# Third party imports

# Local application imports
from .apdu import CommandField, CommandApdu

# Definitions


#
# Commands for interchange
#

def GET_RESPONSE(CLA: str, Le: str):
    return CommandApdu.from_dict({CommandField.Class: CLA, CommandField.Instruction: 'C0', CommandField.P1: '00', CommandField.P2: '00', CommandField.Le: Le})


def SELECT(CLA: str, P1: str, P2: str, Identifier: str = None, Le: str = None):
    apdu_dict = {CommandField.Class: CLA, CommandField.Instruction: 'A4',
                 CommandField.P1: P1, CommandField.P2: P2}

    if Identifier is not None:
        apdu_dict[CommandField.Data] = Identifier

    if Le is not None:
        apdu_dict[CommandField.Le] = Le

    return CommandApdu.from_dict(apdu_dict)
