"""encodings.py
"""

# Standard library imports
from enum import StrEnum, IntEnum

# Third party imports

# Local application imports
from common.binary import ByteString
from common.hstr import clean as _clean


# Enum Definitions
class SecureMessaging(IntEnum):
    No = 0x0
    GlobalPlatform = 0x4
    Iso7816 = 0x8
    Iso7816_CMAC = 0xC


class CardPersonalizationLifeCycleData(StrEnum):
    ICFabricator = "IC Fabricator"
    ICType = "IC Type"
    OperatingSystemIdentifier = "Operating System Identifier"
    OperatingSystemReleaseDate = "Operating System Release Date"
    OperatingSystemReleaseLevel = "Operating System Release Level"
    ICFabricationDate = "IC Fabrication Date"
    ICSerialNumber = "IC Serial Number"
    ICBatchIdentifier = "IC Batch Identifier"
    ICModuleFabricator = "IC Module Fabricator"
    ICModulePackagingDate = "IC Module Packaging Date"
    ICCManufacturer = "ICC Manufacturer"
    ICEmbeddingDate = "IC Embedding Date"
    ICPrePersonalizer = "IC Pre-Personalizer"
    ICPrePersonalizationDate = "IC Pre-Personalization Date"
    ICPrePersonalizationEquipmentIdentifier = "IC Pre-Personalization Equipment Identifier"
    ICPersonalizer = "IC Personalizer"
    ICPersonalizationDate = "IC Personalization Date"
    ICPersonalizationEquipmentIdentifier = "IC Personalization Equipment Identifier"


class GetDataObject(StrEnum):
    ListOfApplications = '2F00'
    IssuerIdentificationNumber = '0042'
    CardImageNumber = '0045'
    CardData = '0066'
    KeyInformationTemplate = '00E0'
    CardCapabilityInformation = '0067'
    CurrentSecurityLevel = '00D3'
    SecurityDomainManagerURL = '5F50'
    ConfirmationCounter = '00C2'
    SequenceCounterOfTheDefaultKeyVersionNumber = '00C1'
    CardProductionLifeCycle = '9F7F'


class FileOccurrence(IntEnum):
    FirstOrOnlyOccurrence = 0x00
    NextOccurrence = 0x02


class ApplicationIdentifier(StrEnum):
    GlobalPlatformSecurityDomain = 'A000000151000000'
    Default = ''


# Class Definitions
class ClassByte(ByteString):
    def __init__(self, secure_messaging: SecureMessaging, logical_channel: int):
        match logical_channel:
            case logical_channel if logical_channel < 0:
                raise ValueError(
                    F'Logical channel number out of bound: should be in [0;19], received {logical_channel}')

            case logical_channel if logical_channel <= 3:
                # CLA Byte Coding according to Table 11-11
                _class_byte = 0x80
                _class_byte += secure_messaging
                _class_byte += logical_channel

            case logical_channel if logical_channel <= 19:
                # CLA Byte Coding according to Table 11-12
                _class_byte = 0xC0 if secure_messaging == SecureMessaging.No else 0xE0
                _class_byte += 4 + logical_channel

            case _:
                raise ValueError(
                    F'Logical channel number out of bound: should be in [0;19], received {logical_channel}')

        super().__init__(_class_byte)

        self.__secure_messaging = secure_messaging
        self.__logical_channel = logical_channel

    @property
    def secure_messaging(self) -> SecureMessaging:
        return self.__secure_messaging

    @property
    def logical_channel(self) -> int:
        return self.__logical_channel


def CLA(value: int | str | ByteString) -> ClassByte:
    """CLA(): creates a GlobalPlatform-compliant CLA Byte
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

    if class_byte.is_bit_unset(8):
        # GP CLA Byte must have b8 set
        raise ValueError(F"CLA(): expecting b8 = 1, received {class_byte}")

    if class_byte.is_bit_unset(7):
        # CLA Byte Coding according to Table 11-11
        secure_messaging = SecureMessaging(int(class_byte.mask(0x0C)))
        logical_channel = int(class_byte.mask(0x03))
    else:
        # CLA Byte Coding according to Table 11-12
        secure_messaging = SecureMessaging.No if class_byte.is_bit_unset(
            6) else SecureMessaging.GlobalPlatform
        logical_channel = 4 + int(class_byte.mask(0x0F))

    return ClassByte(secure_messaging, logical_channel)


class CPLC:
    def __init__(self, data: str):
        cplc_data = _clean(
            data, "globalplatform.encodings.CPLC.__init__()", "data")
        if len(cplc_data) != 84:
            raise ValueError(
                F"CPLC data should be 42 bytes, received {len(cplc_data)//2} bytes: {cplc_data}")
        else:
            self.__cplc_data = cplc_data

    def field(self, data: CardPersonalizationLifeCycleData):
        pos, length = _CPLC_DATA_DEFINITION[data]
        return self.__cplc_data[2*pos:2*(pos+length)]

    def dict(self):
        cplc_dict = {}
        for field in CardPersonalizationLifeCycleData:
            cplc_dict[field] = self.field(field)

        return cplc_dict

    def __str__(self):
        return self.__cplc_data


# Helper functions
_CPLC_DATA_DEFINITION = {
    CardPersonalizationLifeCycleData.ICFabricator: (0, 2),
    CardPersonalizationLifeCycleData.ICType: (2, 2),
    CardPersonalizationLifeCycleData.OperatingSystemIdentifier: (4, 2),
    CardPersonalizationLifeCycleData.OperatingSystemReleaseDate: (6, 2),
    CardPersonalizationLifeCycleData.OperatingSystemReleaseLevel: (8, 2),
    CardPersonalizationLifeCycleData.ICFabricationDate: (10, 2),
    CardPersonalizationLifeCycleData.ICSerialNumber: (12, 4),
    CardPersonalizationLifeCycleData.ICBatchIdentifier: (16, 2),
    CardPersonalizationLifeCycleData.ICModuleFabricator: (18, 2),
    CardPersonalizationLifeCycleData.ICModulePackagingDate: (20, 2),
    CardPersonalizationLifeCycleData.ICCManufacturer: (22, 2),
    CardPersonalizationLifeCycleData.ICEmbeddingDate: (24, 2),
    CardPersonalizationLifeCycleData.ICPrePersonalizer: (26, 2),
    CardPersonalizationLifeCycleData.ICPrePersonalizationDate: (28, 2),
    CardPersonalizationLifeCycleData.ICPrePersonalizationEquipmentIdentifier: (30, 4),
    CardPersonalizationLifeCycleData.ICPersonalizer: (34, 2),
    CardPersonalizationLifeCycleData.ICPersonalizationDate: (36, 2),
    CardPersonalizationLifeCycleData.ICPersonalizationEquipmentIdentifier: (38, 4),
}
