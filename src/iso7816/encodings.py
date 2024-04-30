"""encodings.py
"""

# Standard library imports
from enum import StrEnum, IntEnum

# Third party imports

# Local application imports
from common.binary import ByteString


# Enum Definitions
class TransmissionProtocol(StrEnum):
    T0 = 'T=0'
    T1 = 'T=1'


class SecureMessaging(IntEnum):
    No = 0x0
    Proprietary = 0x4
    Iso7816 = 0x8
    Iso7816_CMAC = 0xC


class Chaining(StrEnum):
    LastOrOnly = 'The command is the last or only command of a chain'
    NotLast = 'The command is not the last command of a chain'


class Selection(IntEnum):
    SelectMForDForEF = 0x00
    SelectChildDF = 0x01
    SelectEFUnderCurrentDF = 0x02
    SelectParentDFOfCurrentDF = 0x03
    SelectByDFName = 0x04
    SelectFromMF = 0x08
    SelectFromCurrentDF = 0x09


class FileOccurrence(IntEnum):
    FirstOrOnlyOccurrence = 0x0
    LastOccurrence = 0x1
    NextOccurrence = 0x2
    PreviousOccurrence = 0x3


class FileControlInformation(IntEnum):
    ReturnFCITemplate = 0x00
    ReturnFCPTempalte = 0x10
    ReturnFMDTemplate = 0x20
    NoResponseOrProprietary = 0x30


# Class definitions
class ClassByte(ByteString):
    def __init__(self, secure_messaging: SecureMessaging, logical_channel: int, command_chaining: Chaining):
        match logical_channel:
            case logical_channel if logical_channel < 0:
                raise ValueError(
                    F'Logical channel number out of bound: should be in [0;19], received {logical_channel}')

            case logical_channel if logical_channel <= 3:
                # CLA Byte Coding according to Table 2
                _class_byte = secure_messaging
                _class_byte += logical_channel

            case logical_channel if logical_channel <= 19:
                # CLA Byte Coding according to Table 3
                _class_byte = 0x40 if secure_messaging == SecureMessaging.No else 0x60
                _class_byte += 4 + logical_channel

            case _:
                raise ValueError(
                    F'Logical channel number out of bound: should be in [0;19], received {logical_channel}')

        if command_chaining == Chaining.NotLast:
            _class_byte += 0x10

        super().__init__(_class_byte)

        self.__secure_messaging = secure_messaging
        self.__logical_channel = logical_channel
        self.__command_chaining = command_chaining

    @property
    def secure_messaging(self) -> SecureMessaging:
        return self.__secure_messaging

    @property
    def logical_channel(self) -> int:
        return self.__logical_channel

    @property
    def chaining(self) -> Chaining:
        return self.__command_chaining


def CLA(value: int | str | ByteString) -> ClassByte:
    """CLA(): creates an ISO7816-compliant CLA Byte
    """
    match value:
        case int():
            class_byte = ByteString(value)
        case str():
            class_byte = ByteString(value)
        case ByteString():
            class_byte = value

        case _:
            raise TypeError(
                F"CLA()| type {type(value)} not supported for argument value")

    if len(class_byte) != 1:
        raise ValueError(
            F"CLA()| expecting 1 byte, received {class_byte} bytes")

    if class_byte.is_bit_set(8):
        # ISO7816 CLA Byte must not have b8 set
        raise ValueError(F"CLA(): expecting b8 = 0, received {class_byte}")

    if class_byte.is_bit_unset(7):
        # CLA Byte Coding according to Table 2
        secure_messaging = SecureMessaging(int(class_byte.mask(0x0C)))
        logical_channel = int(class_byte.mask(0x03))
    else:
        # CLA Byte Coding according to Table 3
        secure_messaging = SecureMessaging.Iso7816 if class_byte.is_bit_set(
            6) else SecureMessaging.No
        logical_channel = 4 + int(class_byte.mask(0x0F))

    command_chaining = Chaining.LastOrOnly if class_byte.is_bit_unset(
        5) else Chaining.NotLast

    return ClassByte(secure_messaging, logical_channel, command_chaining)


class LengthFieldNc(ByteString):
    def __init__(self, Nc: int):
        match Nc:
            case n if n < 0:
                raise ValueError(
                    F"LengthFieldNc(): Ne must be > 0, received {Nc}")

            case 0:
                raise ValueError(F"LengthFieldNc(): Nc cannot be 0")

            case n if n < 256:
                super().__init__(F"{Nc:02X}")

            case n if n < 65536:
                super().__init__(F"00{Nc:04X}")

            case _:
                raise ValueError(
                    F"LengthFieldNc(): Nc must be < 65536, received {Nc}")


class LengthFieldNe(ByteString):
    def __init__(self, Ne: int):
        match Ne:
            case n if n < 0:
                raise ValueError(
                    F"LengthFieldNe(): Ne must be > 0, received {Ne}")

            case 0:
                raise ValueError(F"LengthFieldNe(): Ne cannot be 0")

            case n if n < 256:
                super().__init__(F"{Ne:02X}")

            case 256:
                super().__init__("00")

            case n if n < 65536:
                super().__init__(F"00{Ne:04X}")

            case 65536:
                super().__init__("000000")

            case _:
                raise ValueError(
                    F"LengthFieldNe(): Ne must be <= 65536, received {Ne}")


# Functions
def Lc(data_field: ByteString) -> LengthFieldNc:
    return LengthFieldNc(len(data_field))


Le = LengthFieldNe
