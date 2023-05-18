"""descriptors.py
"""
# Standard library imports
from array import array
from typing import Union
from copy import deepcopy
from enum import IntEnum

# Third party imports

# Local application imports
from common.intlist import to_hstr


# Enum definitions
class DescriptorType(IntEnum):
    Device = 1
    Configuration = 2
    String = 3
    Interface = 4
    Endpoint = 5
    DeviceQualifier = 6
    OtherSpeedConfiguration = 7
    InterfacePower = 8
    SmartCardDevice = 0x21


class EndpointDirection(IntEnum):
    Out = 0x00
    In = 0x80


class EndpointTransfertType(IntEnum):
    Control = 0x00
    Isochronous = 0x01
    Bulk = 0x02
    Interrupt = 0x03


class CcidFeatures(IntEnum):
    NoSpecialCharacteristics = 0x00000000
    AutomaticParameterConfigurationBasedOnAtrData = 0x00000002
    AutomaticActivationOfIccOnInserting = 0x00000004
    AutomaticIccVoltageSelection = 0x00000008
    AutomaticIccClockFrequencyChangeAccordingToActiveParametersProvidedByTheHostOrSelfDetermined = 0x00000010
    AutomaticBaudRateChangeAccordingToActiveParametersProvidedByTheHostOrSelfDetermined = 0x00000020
    AutomaticParametersNegotiationMadeByTheCcid = 0x00000040
    AutomaticPpsMadeByTheCcidAccordingToTheActiveParameters = 0x00000080
    CcidCanSetIccInClockStopMode = 0x00000100
    NadValueOtherThan00AcceptedForT1 = 0x00000200
    AutomaticIfsdExchangeAsFirstExchangeForT1 = 0x00000400
    TpduLevelExchangeWithCcid = 0x00010000
    ShortApduLevelExchangesWithCcid = 0x00020000
    ShortAndExtendedApduLevelExchangesWithCcid = 0x00040000
    UsbWakeUpSignalingSupportedOnCardInsertionAndRemoval = 0x00100000


# Class definitions
class DeviceDescriptor:
    def __init__(self, descriptor: Union[array, list[int]]):
        if descriptor[1] != DescriptorType.Device.value:
            raise ValueError(
                F"Expecting Device descriptor type 01, received {descriptor[1]:02X} ({DescriptorType(descriptor[1]).name})")

        if isinstance(descriptor, array):
            self._descriptor = descriptor[0:descriptor[0]]
        elif isinstance(descriptor, list):
            self._descriptor = array('B', descriptor[0:descriptor[0]])
        else:
            raise TypeError(
                F"Message should be array or list[int], received {type(descriptor)}")

    @property
    def bDeviceClass(self):
        return self._descriptor[4]

    @property
    def idVendor(self):
        return self._descriptor[8:10]

    @property
    def idProduct(self):
        return self._descriptor[10:12]

    @property
    def bNumConfigurations(self):
        return self._descriptor[17]

    @property
    def vendor(self):
        return F"{int.from_bytes(self.idVendor, byteorder='little'):04X}"

    @property
    def product(self):
        return F"{int.from_bytes(self.idProduct, byteorder='little'):04X}"

    def __str__(self):
        return to_hstr(self._descriptor)


class ConfigurationDescriptor:
    def __init__(self, descriptor: Union[array, list[int]]):
        if descriptor[1] != DescriptorType.Configuration.value:
            raise ValueError(
                F"Expecting Configuration descriptor type 02, received {descriptor[1]:02X} ({DescriptorType(descriptor[1]).name})")

        if isinstance(descriptor, array):
            self._descriptor = descriptor[0:descriptor[0]]
        elif isinstance(descriptor, list):
            self._descriptor = array('B', descriptor[0:descriptor[0]])
        else:
            raise TypeError(
                F"Message should be array or list[int], received {type(descriptor)}")

    @property
    def wTotalLength(self):
        return self._descriptor[2:4]

    @property
    def bNumInterfaces(self):
        return self._descriptor[4]

    @property
    def bConfigurationValue(self):
        return self._descriptor[5]

    @property
    def total_length(self):
        return int.from_bytes(self.wTotalLength, byteorder='little')

    def __str__(self):
        return to_hstr(self._descriptor)


class InterfaceDescriptor:
    def __init__(self, descriptor: Union[array, list[int]]):
        if descriptor[1] != DescriptorType.Interface.value:
            raise ValueError(
                F"Expecting Interface descriptor type 02, received {descriptor[1]:02X} ({DescriptorType(descriptor[1]).name})")

        if isinstance(descriptor, array):
            self._descriptor = descriptor[0:descriptor[0]]
        elif isinstance(descriptor, list):
            self._descriptor = array('B', descriptor[0:descriptor[0]])
        else:
            raise TypeError(
                F"Message should be array or list[int], received {type(descriptor)}")

    @property
    def bInterfaceNumber(self):
        return self._descriptor[2]

    @property
    def bNumEndpoints(self):
        return self._descriptor[4]

    @property
    def bInterfaceClass(self):
        return self._descriptor[5]

    def __str__(self):
        return to_hstr(self._descriptor)


class EndpointDescriptor:
    def __init__(self, descriptor: Union[array, list[int]]):
        if descriptor[1] != DescriptorType.Endpoint.value:
            raise ValueError(
                F"Expecting Endpoint descriptor type 05, received {descriptor[1]:02X} ({DescriptorType(descriptor[1]).name})")

        if isinstance(descriptor, array):
            self._descriptor = descriptor[0:descriptor[0]]
        elif isinstance(descriptor, list):
            self._descriptor = array('B', descriptor[0:descriptor[0]])
        else:
            raise TypeError(
                F"Message should be array or list[int], received {type(descriptor)}")

    @property
    def bEndpointAddress(self):
        return self._descriptor[2]

    @property
    def bmAttributes(self):
        return self._descriptor[3]

    @property
    def wMaxPacketSize(self):
        return self._descriptor[4:6]

    @property
    def bInterval(self):
        return self._descriptor[6]

    @property
    def number(self):
        return self.bEndpointAddress & 0x0F

    @property
    def direction(self):
        return EndpointDirection(self.bEndpointAddress & 0x80)

    @property
    def transfert_type(self):
        return EndpointTransfertType(self.bmAttributes & 0x03)

    @property
    def maximum_packet_size(self):
        return int.from_bytes(self.wMaxPacketSize, byteorder='little') & 0x07FF

    def __str__(self):
        return to_hstr(self._descriptor)


class SmartCardDeviceDescriptor:
    def __init__(self, descriptor: Union[array, list[int]]):
        if descriptor[1] != DescriptorType.SmartCardDevice.value:
            raise ValueError(
                F"Expecting Smart Card Device descriptor type 21, received {descriptor[1]:02X} ({DescriptorType(descriptor[1]).name})")

        if descriptor[0] != 0x36:
            raise ValueError(
                F"Smart Card Device descriptor should be 54 bytes, received {descriptor[0]:02X} ({to_hstr(descriptor[0:descriptor[0]])})")

        if isinstance(descriptor, array):
            self._descriptor = descriptor[0:descriptor[0]]
        elif isinstance(descriptor, list):
            self._descriptor = array('B', descriptor[0:descriptor[0]])
        else:
            raise TypeError(
                F"Message should be array or list[int], received {type(descriptor)}")

    @property
    def bMaxSlotIndex(self):
        return self._descriptor[4]

    @property
    def bVoltageSupport(self):
        return self._descriptor[5]

    @property
    def dwProtocols(self):
        return self._descriptor[6:10]

    @property
    def dwMaxIFSD(self):
        return self._descriptor[28:32]

    @property
    def dwFeatures(self):
        return self._descriptor[40:44]

    @property
    def dwMaxCCIDMessageLength(self):
        return self._descriptor[44:48]

    @property
    def bMaxCCIDBusySlots(self):
        return self._descriptor[53]

    @property
    def features(self):
        _features = int.from_bytes(self.dwFeatures, byteorder='little')
        if _features == 0x00000000:
            return [CcidFeatures.NoSpecialCharacteristics]
        else:
            _features_list = []
            for feature in CcidFeatures:
                if (feature & _features) != 0:
                    _features_list.append(feature)

            return _features_list

    def __str__(self):
        return F"Smart Card Device Class Descriptor: {to_hstr(self._descriptor)}"
