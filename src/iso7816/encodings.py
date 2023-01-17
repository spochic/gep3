"""encodings.py
"""

# Standard library imports
from enum import Enum

# Third party imports

# Local application imports
from common.hstr import clean as _clean


# Enum Definitions

class SecureMessaging(Enum):
    No = 'No SM or no indication'
    Proprietary = 'Proprietary SM format'
    Iso7816 = 'SM according to ISO7816-6 6, command header not processed'
    Iso7816_CMAC = 'SM according to ISO7816-6 6, command header authenticated'


class Chaining(Enum):
    LastOrOnly = 'The command is the last or only command of a chain'
    NotLast = 'The command is not the last command of a chain'


# Class Definitions


class CLA:
    def __init__(self, secure_messaging: SecureMessaging, chaining: Chaining, logical_channel: int):
        if (logical_channel < 0) or (logical_channel > 19):
            raise ValueError(
                F'Logical channel number out of bound: should be in [0;19], received {logical_channel}')

        self.__logical_channel = logical_channel
        self.__chaining = chaining
        self.__secure_messaging = secure_messaging

    @classmethod
    def from_value(cls, CLA: int):
        if (CLA < 0x00) or (CLA > 0xFF):
            raise ValueError(
                F'Class byte should out of bound: should be 2 bytes, received {CLA:X}')

        secure_messaging: SecureMessaging

        chaining: Chaining
        if CLA & 0x10 == 0x00:
            chaining = Chaining.LastOrOnly
        else:
            chaining = Chaining.NotLast

        logical_channel: int

        # Testing b7
        if CLA & 0x40 == 0x00:
            # CLA Byte Coding according to Table 2
            # Testing b4-b3
            match CLA & 0x0C:
                case 0x00:
                    secure_messaging = SecureMessaging.No
                case 0x04:
                    secure_messaging = SecureMessaging.Proprietary
                case 0x08:
                    secure_messaging = SecureMessaging.Iso7816
                case 0x0C:
                    secure_messaging = SecureMessaging.Iso7816_CMAC
                case _:
                    # This should not happen
                    raise ArithmeticError(
                        F'CLA.from_value() error: CLA = {CLA:02X}')

            logical_channel = CLA & 0x03

        else:
            # CLA Byte Coding according to Table 3
            # Testing b6
            if CLA & 0x20 == 0x00:
                secure_messaging = SecureMessaging.No
            else:
                secure_messaging = SecureMessaging.Iso7816

            logical_channel = CLA & 0x0F

        return cls(secure_messaging, chaining, logical_channel)

    @classmethod
    def from_string(cls, CLA: str):
        return cls.from_value(cls, int(_clean(CLA), 16))

    def value(self) -> int:
        CLA = 0x00

        if self.__logical_channel <= 3:
            # CLA Byte Coding according to Table 11-11
            CLA += self.__logical_channel
            match self.__secure_messaging:
                case SecureMessaging.No:
                    CLA += 0x00
                case SecureMessaging.Proprietary:
                    CLA += 0x04
                case SecureMessaging.Iso7816:
                    CLA += 0x08
                case SecureMessaging.Iso7816_CMAC:
                    CLA += 0x0C

        else:
            # CLA Byte Coding according to Table 11-12
            CLA += 0x40 + self.__logical_channel
            if self.__secure_messaging != SecureMessaging.No:
                CLA += 0x20

        if self.__chaining == Chaining.NotLast:
            CLA += 0x10

        return CLA

    def str(self) -> str:
        return F"{self.value():02X}"
