# Standard library imports
from enum import IntEnum
from array import array

# Third party imports

# Local application imports
from .bulk_message import BulkOutMessage


# Definitions
class PowerSelection(IntEnum):
    AutomaticVoltageSelection = 0x00
    Volts_5_0 = 0x01
    Volts_3_0 = 0x02
    Volts_1_8 = 0x03

    def __str__(self):
        match self:
            case PowerSelection.AutomaticVoltageSelection:
                return 'Automatic power selection'

            case PowerSelection.Volts_5_0:
                return '5V'

            case PowerSelection.Volts_3_0:
                return '3V'

            case PowerSelection.Volts_1_8:
                return '1.8V'


class PC_to_RDR_GetSlotStatus(BulkOutMessage):
    def __init__(self, bSlot: int, bSeq: int):
        msg = [0x65, 0x00, 0x00, 0x00, 0x00, bSlot, bSeq,
               0x00, 0x00, 0x00]
        super().__init__(array('B', msg))


class PC_to_RDR_IccPowerOn(BulkOutMessage):
    def __init__(self, bSlot: int, bSeq: int, bPowerSelect: PowerSelection):
        msg = [0x62, 0x00, 0x00, 0x00, 0x00, bSlot, bSeq,
               bPowerSelect, 0x00, 0x00]
        super().__init__(array('B', msg))

    @property
    def power_select(self):
        return PowerSelection(self.bPowerSelect)

    @property
    def bPowerSelect(self):
        return self.array[7]

    def __str__(self):
        return F"{super().__str__()}, {self.power_select.name}"


class PC_to_RDR_IccPowerOff(BulkOutMessage):
    def __init__(self, bSlot: int, bSeq: int):
        msg = [0x63, 0x00, 0x00, 0x00, 0x00, bSlot, bSeq, 0x00, 0x00, 0x00]
        super().__init__(array('B', msg))


class PC_to_RDR_Abort(BulkOutMessage):
    def __init__(self, bSlot: int, bSeq: int):
        msg = [0x72, 0x00, 0x00, 0x00, 0x00, bSlot, bSeq, 0x00, 0x00, 0x00]
        super().__init__(array('B', msg))


class PC_to_RDR_XfrBlock(BulkOutMessage):
    def __init__(self, bSlot: int, bSeq: int, bBWI: int, wLevelParameter: list[int], abData: list[int]):
        dwLength = list(int.to_bytes(len(abData), 4, byteorder='little'))
        msg = [0x6F] + dwLength + [bSlot, bSeq, bBWI] + \
            wLevelParameter + abData
        super().__init__(array('B', msg))


class PC_to_RDR_GetParameters(BulkOutMessage):
    def __init__(self, bSlot, bSeq):
        super().__init__(
            array('B', [0x6C, 0x00, 0x00, 0x00, 0x00, bSlot, bSeq, 0x00, 0x00, 0x00]))
