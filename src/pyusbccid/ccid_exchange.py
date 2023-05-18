"""
"""
# Standard library imports

# Third party imports

# Local application imports
from pyusbccid.ifd import InterfaceDevice
from ccid import PC_to_RDR_GetParameters, PC_to_RDR_GetSlotStatus, PC_to_RDR_IccPowerOff, PC_to_RDR_IccPowerOn, PC_to_RDR_XfrBlock,\
    RDR_to_PC_DataBlock, RDR_to_PC_Parameters, RDR_to_PC_SlotStatus,\
    PowerSelection, CommandStatus, IccStatus


# Function definitions
def get_slot_status(ifd: InterfaceDevice, timeout=None) -> RDR_to_PC_SlotStatus:
    msg_out = PC_to_RDR_GetSlotStatus(ifd.bSlot, ifd.bSeq)
    msg_in: RDR_to_PC_SlotStatus = ifd.send_bulk_message(msg_out, timeout)

    return msg_in


def icc_power_on(ifd: InterfaceDevice, bPowerSelect: PowerSelection, timeout=None) -> RDR_to_PC_DataBlock:
    msg_out = PC_to_RDR_IccPowerOn(ifd.bSlot, ifd.bSeq, bPowerSelect)
    msg_in: RDR_to_PC_DataBlock = ifd.send_bulk_message(msg_out, timeout)

    return msg_in


def get_parameters(ifd: InterfaceDevice, timeout=None) -> RDR_to_PC_Parameters:
    msg_out = PC_to_RDR_GetParameters(ifd.bSlot, ifd.bSeq)
    msg_in: RDR_to_PC_Parameters = ifd.send_bulk_message(msg_out, timeout)

    return msg_in


def icc_power_off(ifd: InterfaceDevice, timeout=None) -> RDR_to_PC_SlotStatus:
    msg_out = PC_to_RDR_IccPowerOff(ifd.bSlot, ifd.bSeq)
    msg_in: RDR_to_PC_SlotStatus = ifd.send_bulk_message(msg_out, timeout)

    return msg_in


def xfr_block(ifd: InterfaceDevice, data: list[int], timeout=None) -> RDR_to_PC_DataBlock:
    msg_out = PC_to_RDR_XfrBlock(ifd.bSlot,
                                 ifd.bSeq,
                                 0,
                                 [0x00, 0x00],
                                 data)
    msg_in: RDR_to_PC_DataBlock = ifd.send_bulk_message(msg_out, timeout)

    return msg_in


def cold_reset(ifd: InterfaceDevice, bPowerSelect: PowerSelection, timeout=None):
    slot_status: RDR_to_PC_SlotStatus = get_slot_status(ifd, timeout)
    message_log = [slot_status]

    if slot_status.command_status != CommandStatus.ProcessedWithoutError:
        # Abort if Get Slot Status processed with error
        return {}, message_log

    # CommandStatus.ProcessedWithoutError
    if slot_status.icc_status in [IccStatus.NoIccPresent, IccStatus.RFU]:
        # Abort if no card present or RFU
        message_log.append(slot_status)
        return {}, message_log

    # IccStatus.IccPresentAndActive or IccStatus.IccPresentAndInactive
    if slot_status.icc_status == IccStatus.IccPresentAndActive:
        # Card already powered, must be powered down first
        slot_status: RDR_to_PC_SlotStatus = icc_power_off(ifd, timeout)
        message_log.append(slot_status)
        response, message_log_2 = cold_reset(ifd, bPowerSelect, timeout)
        return response, message_log + message_log_2

    # IccStatus.IccPresentAndInactive
    power_on: RDR_to_PC_DataBlock = icc_power_on(
        ifd, bPowerSelect, timeout)
    message_log.append(power_on)
    if power_on.command_status != CommandStatus.ProcessedWithoutError:
        return {}, message_log

    response = {'atr': power_on.data}

    parameters: RDR_to_PC_Parameters = get_parameters(ifd, timeout)
    message_log.append(parameters)
    if parameters.command_status != CommandStatus.ProcessedWithoutError:
        return response, message_log

    response['protocol'] = parameters.protocol

    return response, message_log
