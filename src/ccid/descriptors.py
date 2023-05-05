"""descriptors.py
"""
# Standard library imports
from array import array
from typing import Union
from copy import deepcopy

# Third party imports

# Local application imports
from common.intlist import to_hstr


# Class definitions
class SmartCardDeviceClassDescriptor:
    def __init__(self, descriptor: Union[array, list[int]]):
        if len(descriptor) != 0x36:
            raise ValueError(
                F"Smart Card Device Class Descriptor should be 54 bytes, received {len(descriptor)} ({to_hstr(descriptor)})")

        if isinstance(descriptor, array):
            self._descriptor = deepcopy(descriptor)
        elif isinstance(descriptor, list):
            self._descriptor = array('B', descriptor)
        else:
            raise TypeError(
                F"Message should be array or list[int], received {type(descriptor)}")

    def bMaxSlotIndex(self):
        return self._descriptor[4]

    def dwFeatures(self):
        return self._descriptor[40:44]

    def features(self):
        _features = int.from_bytes(self.dwFeatures(), byteorder='little')
        description = []
        if _features & 0x00000002:
            description.append(
                'Automatic parameter configuration based on ATR data')

        if _features & 0x00000004:
            description.append('Automatic activation of ICC on inserting')

        if _features & 0x00000008:
            description.append('Automatic ICC voltage selection')

        if _features & 0x00000040:
            description.append(
                'Automatic parameters negotiation made by the CCID')

        if _features & 0x00000080:
            description.append(
                'Automatic PPS made by the CCID according to the active parameters')

        if _features & 0x00010000:
            description.append('TPDU level exchanges with CCID')

        if _features & 0x00020000:
            description.append('Short APDU level exchange with CCID')

        if _features & 0x00040000:
            description.append(
                'Short and Extended APDU level exchange with CCID')

        return ', '.join(description)

    def __str__(self):
        return F"Smart Card Device Class Descriptor: {to_hstr(self._descriptor)}"
