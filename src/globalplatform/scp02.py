"""scp02.py
"""

# Standard library imports
from enum import StrEnum

# Third party imports

# Local application imports
from common.binary import ByteString
from iso7816.apdu import CommandApdu, ResponseApdu
from crypto.des import tdea_2_ede_cbc, mac_2_ede


# Secure Channel Protocol '02' encodings defined by GP
class SecurityLevel(StrEnum):
    NoSecureMessagingExpected = '00'
    C_MAC = '01'
    C_DECRYPTIONandC_MAC = '03'
    R_MAC = '10'
    C_MACandR_MAC = '11'
    C_DECRYPTIONandC_MACandR_MAC = '13'


# CARD AUTHENTICATION CRYPTOGRAM
def card_challenge(C_MAC_SK: ByteString, AID: ByteString) -> ByteString:
    block = AID + '80'
    if len(block) % 8 != 0:
        block += '00' * (8 - len(block) % 8)
    mac = mac_2_ede(C_MAC_SK, block)
    return mac[0:6]


def card_cryptogram(S_ENC_SK: ByteString, host_challenge: ByteString, sequence_counter: ByteString, card_challenge: ByteString) -> ByteString:
    card_cryptogram_input = host_challenge + \
        sequence_counter + card_challenge + '80' + '00' * 7
    return tdea_2_ede_cbc(S_ENC_SK, card_cryptogram_input, ByteString('00' * 8))[-8:]


# HOST AUTHENTICATION CRYPTOGRAM
def host_cryptogram(S_ENC_SK: ByteString, sequence_counter: ByteString, card_challenge: ByteString, host_challenge: ByteString) -> ByteString:
    host_cryptogram_input = sequence_counter + \
        card_challenge + host_challenge + '80' + '00' * 7
    return tdea_2_ede_cbc(S_ENC_SK, host_cryptogram_input, ByteString('00' * 8))[-8:]


# HOST MAC
def host_mac(C_MAC_SK: ByteString, host_cryptogram: ByteString) -> ByteString:
    return mac_2_ede(C_MAC_SK, "8482010010" + host_cryptogram + '80' + '00' * 2)


#
# APDUs
#
# Secure Channel Protocol '02' command APDUs defined by GP
class InitializeUpdate(CommandApdu):
    def __init__(self, CLA: ByteString, key_version_number: ByteString, host_challenge: ByteString):
        if len(host_challenge) != 8:
            raise ValueError(
                F"INITIALIZE UPDATE: host cryptogram should be 8 bytes, received '{host_challenge}'")

        return super().__init__(CLA, ByteString('50'), key_version_number, ByteString('00'), data_field=host_challenge, Ne=256)


def INITIALIZE_UPDATE(CLA: ByteString, key_version_number: ByteString, host_challenge: ByteString):
    return InitializeUpdate(CLA, key_version_number, host_challenge)


class InitializeUpdateResponse(ResponseApdu):
    def __init__(self, response: ByteString):
        if len(response) != 30:
            raise ValueError(
                F"INITIALIZE UPDATE: response should be 30 bytes, received '{response}'")

        return super().__init__(response)

    @property
    def key_diversification_data(self):
        return self[0:10]

    @property
    def key_information(self):
        return self[10:12]

    @property
    def sequence_counter(self):
        return self[12:14]

    @property
    def card_challenge(self):
        return self[14:20]

    @property
    def card_cryptogram(self):
        return self[20:28]


class ExternalAuthenticate(CommandApdu):
    def __init__(self, CLA: ByteString, security_level: SecurityLevel, host_cryptogram: ByteString, MAC: ByteString):
        if len(host_cryptogram) != 8:
            raise ValueError(
                F"EXTERNAL AUTHENTICATE: host cryptogram should be 8 bytes, received '{host_cryptogram}'")

        if len(MAC) != 8:
            raise ValueError(
                F"EXTERNAL AUTHENTICATE: MAC should be 8 bytes, received '{MAC}'")

        return super().__init__(CLA, ByteString('82'), ByteString(security_level.value), ByteString('00'), data_field=host_cryptogram+MAC, Ne=None)


def EXTERNAL_AUTHENTICATE(CLA: ByteString, security_level: ByteString, host_cryptogram: ByteString, MAC: ByteString):
    return ExternalAuthenticate(CLA, SecurityLevel(security_level), host_cryptogram, MAC)
