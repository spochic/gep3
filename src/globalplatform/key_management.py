"""key_management.py
"""

# Standard library imports

# Third party imports

# Local application imports
from common.binary import ByteString
from crypto.des import tdea_2_ede_ecb, tdea_2_ede_cbc


# CARD KEYS
def S_ENC_DK(S_ENC_KMC: ByteString, derivation_id: ByteString):
    return tdea_2_ede_ecb(S_ENC_KMC, ByteString(F"{derivation_id}F001{derivation_id}0F01"))


def S_MAC_DK(S_MAC_KMC: ByteString, derivation_id: ByteString):
    return tdea_2_ede_ecb(S_MAC_KMC, ByteString(F"{derivation_id}F002{derivation_id}0F02"))


def DEK_DK(DEK_KMC: ByteString, derivation_id: ByteString):
    return tdea_2_ede_ecb(DEK_KMC, ByteString(F"{derivation_id}F003{derivation_id}0F03"))


# SESSION KEYS
def C_MAC_SK(S_MAC_DK: ByteString, sequence_counter: ByteString):
    return tdea_2_ede_cbc(S_MAC_DK, ByteString(F"0101{sequence_counter}" + "00" * 12), ByteString('00' * 8))


def R_MAC_SK(S_MAC_DK: ByteString, sequence_counter: ByteString):
    return tdea_2_ede_cbc(S_MAC_DK, ByteString(F"0102{sequence_counter}" + "00" * 12), ByteString('00' * 8))


def S_ENC_SK(S_ENC_DK: ByteString, sequence_counter: ByteString):
    return tdea_2_ede_cbc(S_ENC_DK, ByteString(F"0182{sequence_counter}" + "00" * 12), ByteString('00' * 8))


def DEK_SK(DEK_DK: ByteString, sequence_counter: ByteString):
    return tdea_2_ede_cbc(DEK_DK, ByteString(F"0181{sequence_counter}" + "00" * 12), ByteString('00' * 8))
