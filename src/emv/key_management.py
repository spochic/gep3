"""key_management.py
"""

# Standard library imports

# Third party imports
try:
    from icecream import ic
    ic.disable()
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

# Local application imports
from common import hstr
from common.binary import ByteString
from crypto import des


# Function definitions
def master_key_derivation_A(imk: ByteString, pan: str, psn: str = '00'):
    """master_key_derivation_A(): ICC Master Key derivation (Option A)
    """
    X = pan + psn
    if len(X) < 16:
        X = '0' * (16 - len(X)) + X

    Y = ByteString(X[-16:])
    ic(X, Y)

    Zl = des.adjust_parity(des.tdea_2_ede(imk, Y))
    Zr = des.adjust_parity(des.tdea_2_ede(imk, ~Y))
    ic(Zl, Zr)

    return Zl + Zr
