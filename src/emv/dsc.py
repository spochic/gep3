"""dsc.py: Dynamic Security Codes module
"""

# Standard library imports

# Third party imports
try:
    from icecream import ic
    ic.disable()
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa

# Local application imports
from common.binary import ByteString, HexString
from crypto import des


# Function definitions
def generate_dcvv(udk: ByteString, pan: str, atc: str, expiration_date: str, *, service_code='000'):
    alternate_pan = F"{atc}{pan[4:]}"
    ic(alternate_pan)

    input_block = HexString(
        F"{alternate_pan}{expiration_date}{service_code}").rpad(32).bytestring

    udk_a = udk[0:8]
    udk_b = udk[8:16]
    block_a = input_block[0:8]
    block_b = input_block[8:16]
    ic(block_a, block_b)

    block_c = des.dea_e(udk_a, block_a)
    block_d = block_c ^ block_b
    block_e = des.dea_e(udk_a, block_d)
    block_f = des.dea_d(udk_b, block_e)
    block_g = des.dea_e(udk_a, block_f)
    assert block_g == des.mac_2_ede(udk, input_block)
    block_h = block_g.dscan_decimalize
    ic(block_c, block_d, block_e, block_f, block_g, block_h)

    return block_h[0:3]


def generate_ivcvc3(udk: ByteString, track: str) -> str:
    if (len(track) % 16) == 0:
        block = track + "8000000000000000"
    else:
        block = track + "80" + "0" * (16 - len(track) % 16 - 2)
    ic(block)

    mac = des.mac_2_ede(udk, ByteString(block))
    ic(mac)

    return str(mac[-2:])


def generate_cvc3(udk: ByteString, block: str) -> str:
    cryptogram = des.tdea_2_ede(udk, ByteString(block))
    ic(cryptogram)
    return F"{int(cryptogram[-2:]):05d}"
