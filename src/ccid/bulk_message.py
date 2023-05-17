# Standard library imports
from enum import IntEnum
from array import array
from copy import deepcopy
from typing import Union

# Third party imports

# Local application imports
from common.intlist import to_hstr as _to_hstr


# Definitions
class MessageType(IntEnum):
    PC_to_RDR_IccPowerOn = 0x62
    PC_to_RDR_IccPowerOff = 0x63
    PC_to_RDR_GetSlotStatus = 0x65
    PC_to_RDR_GetParameters = 0x6C
    PC_to_RDR_XfrBlock = 0x6F
    PC_to_RDR_Abort = 0x72
    RDR_to_PC_DataBlock = 0x80
    RDR_to_PC_SlotStatus = 0x81
    RDR_to_PC_Parameters = 0x82


class IccStatus(IntEnum):
    IccPresentAndActive = 0
    IccPresentAndInactive = 1
    NoIccPresent = 2
    RFU = 3


class CommandStatus(IntEnum):
    ProcessedWithoutError = 0
    Failed = 1
    TimeExtensionRequested = 2
    RFU = 3


class SlotError:
    def __init__(self, bError: int = None):
        self._bError = bError

    def __str__(self):
        error_str = {0xFF: "CMD_ABORTED (Host aborted the current activity)",
                     0xFE: "ICC_MUTE (CCID timed out while talking to the ICC)",
                     0xFD: "XFR_PARITY_ERROR (Parity error while talking to the ICC)",
                     0xFC: "XFR_OVERRUN (Overrun error while talking to the ICC)",
                     0xFB: "HW_ERROR (An all inclusive hardware error occurred)",
                     0xF8: "BAD_ATR_TS",
                     0xF7: "BAD_ATR_TCK",
                     0xF6: "ICC_PROTOCOL_NOT_SUPPORT ED",
                     0xF5: "ICC_CLASS_NOT_SUPPORTED",
                     0xF4: "PROCEDURE_BYTE_CONFLICT",
                     0xF3: "DEACTIVATED_PROTOCOL",
                     0xF2: "BUSY_WITH_AUTO_SEQUENCE (Automatic Sequence Ongoing)",
                     0xF0: "PIN_TIMEOUT",
                     0xEF: "PIN_CANCELLED",
                     0xE0: "CMD_SLOT_BUSY (A second command was sent to a slot which was already processing a command)",
                     0x00: "Command not supported"}.get(self._bError, None)

        if error_str is not None:
            return error_str
        elif self._bError >= 0x81 and self._bError <= 0xC0:
            return F"User defined error: {self._bError:02X}"
        elif self._bError >= 0x01 and self._bError <= 0x7F:
            return F"Unsupported or incorrect message parameter at index {self._bError:02X}"
        else:
            return "RFU"


class Protocol(IntEnum):
    T0 = 0x00
    T1 = 0x01
    TwoWire = 0x80
    ThreeWire = 0x81
    I2C = 0x82

    def __str__(self):
        match self:
            case Protocol.T0:
                return "T=0"
            case Protocol.T1:
                return "T=1"
            case _:
                return self.name


class BulkMessage:
    def __init__(self, message: Union[list[int], array]):
        if isinstance(message, array):
            self._message = deepcopy(message)
        elif isinstance(message, list):
            self._message = array('B', message)
        else:
            raise TypeError(
                F"Message should be array or list[int], received {type(message)}")

    @property
    def array(self) -> array:
        return deepcopy(self._message)

    @property
    def string(self) -> str:
        return _to_hstr(self._message)

    @property
    def header(self) -> str:
        return _to_hstr(self._message[0:10])

    @property
    def data(self) -> str:
        return _to_hstr(self._message[10:])

    @property
    def message_type(self) -> MessageType:
        return MessageType(self._message[0])

    @property
    def length(self) -> int:
        return int.from_bytes(self._message[1:5], byteorder='little')

    @property
    def bMessageType(self) -> int:
        return self._message[0]

    @property
    def dwLength(self) -> array:
        return self._message[1:5]

    @property
    def bSlot(self) -> int:
        return self._message[5]

    @property
    def bSeq(self) -> int:
        return self._message[6]

    def __str__(self):
        message_str = self.string
        content_hex = F"{message_str[0:2]} {message_str[2:10]} {message_str[10:12]} {message_str[12:14]} {message_str[14:]}"
        return F"{self.message_type.name} ({content_hex}): bSlot={message_str[10:12]}, bSeq={message_str[12:14]}"


class BulkOutMessage(BulkMessage):
    pass


class BulkInMessage(BulkMessage):
    @property
    def icc_status(self):
        return IccStatus(self.bStatus & 0x03)

    @property
    def command_status(self):
        return CommandStatus(self.bStatus >> 6)

    @property
    def error(self):
        if self.command_status == CommandStatus.Failed:
            return SlotError(self.bError)
        else:
            return SlotError()

    @property
    def bStatus(self):
        return self._message[7]

    @property
    def bError(self):
        return self._message[8]

    def __str__(self):
        if self.command_status == CommandStatus.Failed:
            return F"{super().__str__()}, {self.command_status.name}, {self.error}, {self.icc_status.name}"
        else:
            return F"{super().__str__()}, {self.command_status.name}, {self.icc_status.name}"
