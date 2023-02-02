"""encodings.py
"""

# Standard library imports
from enum import Enum

# Third party imports

# Local application imports
from common.hstr import clean as _clean


# Enum Definitions


class MultosDataField(Enum):
    MultosVersionNumber = "MULTOS Version Number"
    ICManufacturerIdentifier = "IC Manufacturer ID"
    ImplementerIdentifier = "Implementer ID"
    MCDIdentifier = "MCD ID"
    ProductIdentifier = "Product ID"
    IssuerIdentifier = "Issuer ID"
    MSMControlsDataDate = "MSM Controls Data Date"
    MCDNumber = "MCD Number"
    RFU = "RFU"
    MaximumDynamicSize = "Maximum Dynamic Size"
    MaximumPublicSize = "Maximum Public Size"
    MaximumDirectoryFileRecordSize = "Maximum DIR File Record Size"
    MaximumFCIRecordSize = "Maximum FCI Record Size"
    MaximumATRHistoricalByteRecordSize = "Maximum ATR Historical Byte Record Size"
    MaximumATRFileRecordSize = "Maximum ATR File Record Size"
    MultosPublicKeyCertificateLength = "MULTOS Public Key Certificate Length"
    SecurityLevel = "Security Level"
    CertificationMethodIdentifier = "Certification Method ID"
    ApplicationSignatureMethodIdentifier = "Application Signature Method ID"
    EnciphermentDescriptor = "Encipherment Descriptor"
    HashMethodIdentifier = "Hash Method ID"


# Class Definitions


class MultosData:
    def __init__(self, data: str):
        multos_data = _clean(
            data, "multos.encodings.MultosData.__init__()", "data")
        if len(multos_data) != 254:
            raise ValueError(
                F"MULTOS data should be 127 bytes, received {len(multos_data)//2} bytes: {multos_data}")
        else:
            self.__multos_data = multos_data

    def get_field(self, data: MultosDataField):
        pos, length = _MULTOS_DATA_DEFINITION[data]
        return self.__multos_data[2*pos:2*(pos+length)]

    def str(self):
        return self.__multos_data


# Helper functions
_MULTOS_DATA_DEFINITION = {
    MultosDataField.MultosVersionNumber: (0, 2),
    MultosDataField.ICManufacturerIdentifier: (2, 1),
    MultosDataField.ImplementerIdentifier: (3, 1),
    MultosDataField.MCDIdentifier: (4, 6),
    MultosDataField.ProductIdentifier: (10, 1),
    MultosDataField.IssuerIdentifier: (11, 4),
    MultosDataField.MSMControlsDataDate: (15, 1),
    MultosDataField.MCDNumber: (16, 8),
    MultosDataField.RFU: (24, 80),
    MultosDataField.MaximumDynamicSize: (104, 2),
    MultosDataField.MaximumPublicSize: (106, 2),
    MultosDataField.MaximumDirectoryFileRecordSize: (108, 2),
    MultosDataField.MaximumFCIRecordSize: (110, 2),
    MultosDataField.MaximumATRHistoricalByteRecordSize: (112, 2),
    MultosDataField.MaximumATRFileRecordSize: (114, 2),
    MultosDataField.MultosPublicKeyCertificateLength: (116, 2),
    MultosDataField.SecurityLevel: (118, 1),
    MultosDataField.CertificationMethodIdentifier: (119, 2),
    MultosDataField.ApplicationSignatureMethodIdentifier: (121, 2),
    MultosDataField.EnciphermentDescriptor: (123, 2),
    MultosDataField.HashMethodIdentifier: (125, 2)

}
