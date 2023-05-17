# Standard library imports
from enum import IntEnum
from typing import Union

# Third party imports

# Local application imports
from .bulk_message import *


# Definitions
class SlotCurrentState(IntEnum):
    NoIccPresent = 0
    IccPresent = 1


class SlotChangedStatus(IntEnum):
    NoChange = 0
    Change = 1


class ClockStatus(IntEnum):
    ClockRunning = 0
    ClockStoppedStateL = 1
    ClockStoppedStateH = 2
    ClockStoppedUnknownState = 3


class RDR_to_PC_NotifySlotChange(BulkInMessage):
    def current_state(self, slot_nr: int) -> SlotCurrentState:
        slot_current_state = (self.bmSlotICCState >> (2 * slot_nr)) & 0x1
        return SlotCurrentState(slot_current_state)

    def changed_status(self, slot_nr: int) -> SlotCurrentState:
        slot_changed_status = (self.bmSlotICCState >>
                               (2 * slot_nr + 1)) & 0x1
        return SlotCurrentState(slot_changed_status)

    @property
    def bmSlotICCState(self):
        return self._message[1]

    def __str__(self):
        return F"{super().__str__()}, {self.current_state().name}, {self.changed_status().name}"


class RDR_to_PC_DataBlock(BulkInMessage):
    def __str__(self):
        if self.command_status == CommandStatus.Failed:
            return F"{super().__str__()}"
        else:
            return F"{super().__str__()}, data={self.data}"

    @property
    def bChainParameter(self):
        return self._message[9]


class RDR_to_PC_SlotStatus(BulkInMessage):
    @property
    def clock_status(self):
        return ClockStatus(self.bClockStatus)

    @property
    def bClockStatus(self):
        return self._message[9]

    def __str__(self):
        return F"{super().__str__()}, {self.clock_status.name}"


class RDR_to_PC_Parameters(BulkInMessage):
    @property
    def protocol(self):
        return Protocol(self.bProtocolNum)

    @property
    def bProtocolNum(self):
        return self._message[9]

    def __str__(self):
        return F"{super().__str__()}, protocol {self.protocol}"


# Functions
def RDR_to_PC(message: Union[array, list[int]]):
    cls = {0x50: RDR_to_PC_NotifySlotChange,
           0x80: RDR_to_PC_DataBlock,
           0x81: RDR_to_PC_SlotStatus,
           0x82: RDR_to_PC_Parameters}.get(message[0], BulkInMessage)

    return cls(message)
