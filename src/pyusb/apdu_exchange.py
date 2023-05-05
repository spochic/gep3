"""
"""
# Standard library imports

# Third party imports

# Local application imports
from .ifd import InterfaceDevice
from .messages_exchange import xfr_block
from ccid import Protocol, PC_to_RDR_XfrBlock
from iso7816 import CommandApdu, ResponseApdu, CommandCase, GetResponse


# Function definitions
def send_apdu(ifd: InterfaceDevice, protocol: Protocol, command_apdu: CommandApdu, timeout=None) -> ResponseApdu:
    match protocol:
        case Protocol.T0:
            match command_apdu.case:
                case CommandCase.Case1:
                    return transmit_apdu(ifd, command_apdu, timeout)

                case CommandCase.Case2s:
                    response_apdu = transmit_apdu(ifd,
                                                  command_apdu, timeout)
                    if response_apdu.SW1() == '6C':
                        # Case 2S.3 — Process aborted; Ne not accepted, Na indicated
                        return transmit_apdu(ifd, command_apdu.updated_Le(response_apdu.SW2()), timeout)
                    else:
                        return response_apdu

                case CommandCase.Case3s:
                    return transmit_apdu(ifd, command_apdu, timeout)

                case CommandCase.Case4s:
                    response_apdu = transmit_apdu(ifd,
                                                  command_apdu, timeout)
                    if response_apdu.SW12() == '9000':
                        # Case 4S.2 — Process completed
                        return transmit_apdu(ifd, GetResponse(command_apdu.CLA(), int(command_apdu.Le(), 16)), timeout)
                    elif response_apdu.SW1() == '61':
                        # Case 4S.3 — Process completed with information added
                        return transmit_apdu(ifd, GetResponse(command_apdu.CLA(), min(int(response_apdu.SW2(), 16), int(command_apdu.Le(), 16))), timeout)
                    else:
                        return response_apdu

                case _:
                    raise ValueError(
                        F"{command_apdu.case.value} not yet implemented for protocol T=0")

        case Protocol.T1:
            return transmit_apdu(ifd, command_apdu, timeout)

        case _:
            raise ValueError(
                F"Unsupported protocol: {protocol.name}")


def transmit_apdu(ifd: InterfaceDevice, command_apdu: CommandApdu, timeout=None) -> ResponseApdu:
    response = xfr_block(ifd, command_apdu.list(), timeout)

    return ResponseApdu(response.data())
