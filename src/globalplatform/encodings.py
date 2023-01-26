"""encodings.py
"""

# Standard library imports
from enum import Enum

# Third party imports

# Local application imports
from common.hstr import clean as _clean


# Enum Definitions

class SecureMessaging(Enum):
    No = 'No secure messaging'
    GlobalPlatform = 'Secure messaging - GlobalPlatform proprietary'
    Iso7816 = 'Secure messaging - ISO7816 standard, command header not processed (no C-MAC)'
    Iso7816_CMAC = 'Secure messaging - ISO7816 standard, command header authenticated (C-MAC)'


class CardPersonalizationLifeCycleData(Enum):
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

# Class Definitions


class CLA:
    def __init__(self, secure_messaging: SecureMessaging, logical_channel: int):
        if (logical_channel < 0) or (logical_channel > 19):
            raise ValueError(
                F'Logical channel number out of bound: should be in [0;19], received {logical_channel}')

        self.__logical_channel = logical_channel
        self.__secure_messaging = secure_messaging

    @classmethod
    def from_value(cls, CLA: int):
        if (CLA < 0x00) or (CLA > 0xFF):
            raise ValueError(
                F'Class byte should out of bound: should be 2 bytes, received {CLA:X}')

        secure_messaging: SecureMessaging
        logical_channel: int

        # Testing b7
        if CLA & 0x40 == 0x00:
            # CLA Byte Coding according to Table 11-11
            # Testing b4-b3
            match CLA & 0x0C:
                case 0x00:
                    secure_messaging = SecureMessaging.No
                case 0x04:
                    secure_messaging = SecureMessaging.GlobalPlatform
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
            # CLA Byte Coding according to Table 11-12
            # Testing b6
            if CLA & 0x20 == 0x00:
                secure_messaging = SecureMessaging.No
            else:
                secure_messaging = SecureMessaging.GlobalPlatform

            logical_channel = CLA & 0x0F

        return cls(secure_messaging, logical_channel)

    @classmethod
    def from_string(cls, CLA: str):
        return cls.from_value(cls, int(_clean(CLA), 16))

    def value(self) -> int:
        CLA = 0x00

        if self.__logical_channel <= 3:
            # CLA Byte Coding according to Table 11-11
            CLA += 0x80 + self.__logical_channel
            match self.__secure_messaging:
                case SecureMessaging.No:
                    CLA += 0x00
                case SecureMessaging.GlobalPlatform:
                    CLA += 0x04
                case SecureMessaging.Iso7816:
                    CLA += 0x08
                case SecureMessaging.Iso7816_CMAC:
                    CLA += 0x0C

        else:
            # CLA Byte Coding according to Table 11-12
            CLA += 0xC0 + self.__logical_channel
            if self.__secure_messaging != SecureMessaging.No:
                CLA += 0x20

        return CLA

    def str(self) -> str:
        return F"{self.value():02X}"


class CPLC:
    def __init__(self, data: str):
        cplc_data = _clean(
            data, "globalplatform.encodings.CPLC.__init__()", "data")
        if len(cplc_data) != 84:
            raise ValueError(
                F"CPLC data should be 42 bytes, received {len(cplc_data)//2} bytes: {cplc_data}")
        else:
            self.__cplc_data = cplc_data

    def get_field(self, data: CardPersonalizationLifeCycleData):
        pos, length = _CPLC_DATA_DEFINITION[data]
        return self.__cplc_data[2*pos:2*(pos+length)]

    def str(self):
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
