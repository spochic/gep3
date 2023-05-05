"""pyusb.py: CCID wrapper for PyUSB
"""
# Standard library imports
import logging

# Third party imports
import usb.core
import usb.util

# Local application imports
from ccid import BulkOutMessage, BulkInMessage, RDR_to_PC, PC_to_RDR_XfrBlock
from iso7816 import CommandApdu, ResponseApdu


# Class definitions
class InterfaceDevice:
    def __init__(self, device: usb.core.Device, interface: usb.core.Interface, cfg_index: int, interface_index: int):
        self.device: usb.core.Device = device
        self._cfg_index = cfg_index
        self._interface_index = interface_index
        self.bSeq: int = 0
        self.bSlot: int = 0

        for endpoint in interface:
            endpoint_type = usb.util.endpoint_type(endpoint.bmAttributes)
            endpoint_direction = usb.util.endpoint_direction(
                endpoint.bEndpointAddress)

            if endpoint_type == usb.util.ENDPOINT_TYPE_BULK and endpoint_direction == usb.util.ENDPOINT_IN:
                self._ep_bulk_in = (endpoint.bEndpointAddress,
                                    endpoint.wMaxPacketSize)
            elif endpoint_type == usb.util.ENDPOINT_TYPE_BULK and endpoint_direction == usb.util.ENDPOINT_OUT:
                self._ep_bulk_out = (
                    endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
            elif endpoint_type == usb.util.ENDPOINT_TYPE_INTR and endpoint_direction == usb.util.ENDPOINT_IN:
                self._ep_intr_in = (endpoint.bEndpointAddress,
                                    endpoint.wMaxPacketSize)
            else:
                raise TypeError(F"Unknown endpoint:\n{endpoint}")

        # Setting name, serial number, and unique identifier
        self.name = usb.util.get_string(
            self.device, self.intf().iInterface)
        if self.name is None:
            self.name = F"{self.device.manufacturer} {self.device.product}"

        self.serial_number = self.device.serial_number
        self.identifier = F"{self.serial_number}.{self._cfg_index}.{self._interface_index}"

        # Checking whether OS driver already attached
        logging.info(F"{self}: Checking whether OS driver is already attached")
        self._reattach = False
        if self.device.is_kernel_driver_active(self._interface_index):
            logging.debug("Detaching kernel driver")
            self._reattach = True
            self.device.detach_kernel_driver(self._interface_index)

    def __del__(self):
        if self._reattach:
            logging.debug("\nReattaching kernel driver")
            self.device.attach_kernel_driver(self._interface_index)

    def cfg(self) -> usb.core.Configuration:
        return self.device[self._cfg_index]

    def intf(self, alternate_setting: int = 0) -> usb.core.Interface:
        return self.cfg()[(self._interface_index, alternate_setting)]

    def write_bulk_message(self, message: BulkOutMessage, timeout=None):
        return self.device.write(self._ep_bulk_out[0], message.array(), timeout)

    def read_bulk_message(self, timeout=None) -> BulkInMessage:
        enpoint_packet_size = self._ep_bulk_in[1]
        endpoint = self._ep_bulk_in[0]

        response_length = 0
        response = usb.util.create_buffer(0)

        n = enpoint_packet_size
        buf = usb.util.create_buffer(enpoint_packet_size)
        while n == enpoint_packet_size:
            n = self.device.read(endpoint, buf, timeout)
            response_length += n
            response += buf

        return RDR_to_PC(response[:response_length])

    def send_bulk_message(self, message: BulkOutMessage, timeout=None) -> BulkInMessage:
        logging.info(F"{self.identifier} --> {message}")
        n = self.write_bulk_message(message, timeout)
        if n != len(message.array()):
            raise AssertionError(
                F"{n} bytes written, expecting {len(message.array())}")

        bSeq_out = message.bSeq()
        bSeq_in = -1
        while bSeq_in != bSeq_out:
            message_in = self.read_bulk_message(timeout)
            logging.info(F"{self.identifier} <-- {message_in}")

            # Getting the sequence number of the incoming message
            bSeq_in = message_in.bSeq()

        self.bSeq = bSeq_in + 1

        return message_in

    def __str__(self):
        return F"{self.name} (serial number = {self.serial_number}, configuration number = {self._cfg_index}, interface number = {self._interface_index})"


# Function defitions
def list_interface_devices() -> list[InterfaceDevice]:
    ccid_devices = usb.core.find(
        find_all=True, custom_match=_find_usb_class(0x0b))
    ifd_list: list[InterfaceDevice] = []

    for ccid_device in ccid_devices:
        for c, cfg in enumerate(ccid_device):
            for i, intf in enumerate(cfg):
                ifd_list.append(InterfaceDevice(ccid_device, intf, c, i))

    return ifd_list


#
# Helper functions
#
class _find_usb_class(object):
    def __init__(self, usb_class):
        self._usb_class = usb_class

    def __call__(self, device: usb.core.Device):
        # 1 Checking class of device
        if device.bDeviceClass == self._usb_class:
            return True
        else:
            # 2 Checking class of each configuration
            for cfg in device:
                # 3 Searching interface with matching class
                intf = usb.util.find_descriptor(
                    cfg, bInterfaceClass=self._usb_class)
                if intf is not None:
                    return True

            else:
                # 4 Return false if none of the configurations have interfaces with matching class
                False
