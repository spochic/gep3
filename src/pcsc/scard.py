"""scard.py
"""

# Standard library imports
import logging
from enum import IntEnum

# Third party imports
from asyncore import read
from smartcard.scard import \
    SCARD_SCOPE_USER as _SCARD_SCOPE_USER,\
    SCARD_SCOPE_SYSTEM as _SCARD_SCOPE_SYSTEM,\
    SCARD_SHARE_SHARED as _SCARD_SHARE_SHARED,\
    SCARD_SHARE_EXCLUSIVE as _SCARD_SHARE_EXCLUSIVE,\
    SCARD_SHARE_DIRECT as _SCARD_SHARE_DIRECT,\
    SCARD_PROTOCOL_T0 as _SCARD_PROTOCOL_T0,\
    SCARD_PROTOCOL_T1 as _SCARD_PROTOCOL_T1,\
    SCARD_PCI_T0 as _SCARD_PCI_T0,\
    SCARD_PCI_T1 as _SCARD_PCI_T1,\
    SCARD_PROTOCOL_RAW as _SCARD_PROTOCOL_RAW,\
    SCARD_LEAVE_CARD as _SCARD_LEAVE_CARD,\
    SCARD_RESET_CARD as _SCARD_RESET_CARD,\
    SCARD_UNPOWER_CARD as _SCARD_UNPOWER_CARD,\
    SCARD_EJECT_CARD as _SCARD_EJECT_CARD,\
    SCARD_S_SUCCESS as _SCARD_S_SUCCESS,\
    INFINITE as _INFINITE,\
    SCARD_STATE_ATRMATCH as _SCARD_STATE_ATRMATCH,\
    SCARD_STATE_UNAWARE as _SCARD_STATE_UNAWARE,\
    SCARD_STATE_IGNORE as _SCARD_STATE_IGNORE,\
    SCARD_STATE_UNAVAILABLE as _SCARD_STATE_UNAVAILABLE,\
    SCARD_STATE_EMPTY as _SCARD_STATE_EMPTY,\
    SCARD_STATE_PRESENT as _SCARD_STATE_PRESENT,\
    SCARD_STATE_EXCLUSIVE as _SCARD_STATE_EXCLUSIVE,\
    SCARD_STATE_INUSE as _SCARD_STATE_INUSE,\
    SCARD_STATE_MUTE as _SCARD_STATE_MUTE,\
    SCARD_STATE_CHANGED as _SCARD_STATE_CHANGED,\
    SCARD_STATE_UNKNOWN as _SCARD_STATE_UNKNOWN,\
    SCARD_ATTR_ATR_STRING as _SCARD_ATTR_ATR_STRING,\
    SCARD_ATTR_VENDOR_IFD_SERIAL_NO as _SCARD_ATTR_VENDOR_IFD_SERIAL_NO,\
    SCARD_ATTR_VENDOR_NAME as _SCARD_ATTR_VENDOR_NAME,\
    SCardEstablishContext as _SCardEstablishContext,\
    SCardListReaders as _SCardListReaders,\
    SCardConnect as _SCardConnect,\
    SCardReconnect as _SCardReconnect,\
    SCardStatus as _SCardStatus,\
    SCardTransmit as _SCardTransmit,\
    SCardDisconnect as _SCardDisconnect,\
    SCardReleaseContext as _SCardReleaseContext,\
    SCardGetErrorMessage as _SCardGetErrorMessage,\
    SCardGetStatusChange as _SCardGetStatusChange,\
    SCardGetAttrib as _SCardGetAttrib


# Local application imports
from common.intlist import to_hstr as _to_hstr
from common.hstr import \
    to_intlist as _to_intlist,\
    minimum as _min,\
    clean as _clean
from iso7816 import CommandApdu, ResponseApdu, CommandCase, GET_RESPONSE as _GET_RESPONSE

# Enum definitions


class Scope(IntEnum):
    User = _SCARD_SCOPE_USER
    System = _SCARD_SCOPE_SYSTEM


class ShareMode(IntEnum):
    Shared = _SCARD_SHARE_SHARED
    Exclusive = _SCARD_SHARE_EXCLUSIVE
    Direct = _SCARD_SHARE_DIRECT


class Protocol(IntEnum):
    T0 = _SCARD_PROTOCOL_T0
    T1 = _SCARD_PROTOCOL_T1
    T0orT1 = _SCARD_PROTOCOL_T0 | _SCARD_PROTOCOL_T1
    Raw = _SCARD_PROTOCOL_RAW


class Disposition(IntEnum):
    LeaveCard = _SCARD_LEAVE_CARD
    ResetCard = _SCARD_RESET_CARD
    UnpowerCard = _SCARD_UNPOWER_CARD
    EjectCard = _SCARD_EJECT_CARD


class State(IntEnum):
    Unknown = 0x0001
    Absent = 0x0002
    Present = 0x0004
    Swallowed = 0x0008
    Powered = 0x0010
    Negotiable = 0x0020
    Specific = 0x0040


class Attribute(IntEnum):
    AtrString = _SCARD_ATTR_ATR_STRING
    IfdSerialNo = _SCARD_ATTR_VENDOR_IFD_SERIAL_NO
    VendorName = _SCARD_ATTR_VENDOR_NAME


# Exception definition

class PcscError(Exception):
    pass


# Functions definitions

def establish_context(dw_scope: Scope):
    """establish_context():
    """
    hresult, hcontext = _SCardEstablishContext(dw_scope)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to establish PC/SC context ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    logging.info(F"PC/SC context established with scope: {dw_scope.name}")
    return hcontext


def list_readers(hcontext, readergroups=None):
    """list_readers():
    """
    if readergroups is None:
        readergroups = []

    hresult, readers = _SCardListReaders(hcontext, readergroups)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to list readers ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    l = len(readers)
    match l:
        case 0:
            logging.info("No reader found")
        case 1:
            logging.info(F"Reader found: {readers[0]}")
        case _:
            logging.info(F"{l} readers found: {', '.join(readers)}")

    return readers


def list_readers_serialno(hcontext, readers):
    """list_readers_serialno():
    """
    serial_nos = []
    for r in readers:
        hcard, _ = connect(hcontext, r, ShareMode.Direct, Protocol.T0orT1)
        serial_nos.append(get_attribute(hcard, Attribute.IfdSerialNo))
        disconnect(hcard, Disposition.UnpowerCard)

    logging.info(
        F"Serial nos listed: {', '.join([F'{r} ({s})' for r,s in zip(readers, serial_nos)])}")
    return serial_nos


def connect(hcontext, reader, dw_share_mode: ShareMode, dw_preferred_protocols: Protocol):
    """connect():
    """
    hresult, hcard, dw_active_protocol = _SCardConnect(
        hcontext, reader, dw_share_mode, dw_preferred_protocols)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Unable to connect ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    protocol = Protocol(dw_active_protocol)

    logging.info(F"Connected with share mode: {dw_share_mode.name}")
    logging.info(F"Connected with active protocol: {protocol.name}")

    return hcard, protocol


def reconnect(hcard, dw_share_mode: ShareMode, dw_preferred_protocols: Protocol, dw_initialization: Disposition):
    """reconnect():
    """
    hresult, dw_active_protocol = _SCardReconnect(
        hcard, dw_share_mode, dw_preferred_protocols, dw_initialization)

    if hresult != _SCARD_S_SUCCESS:
        err = F'Unable to reconnect ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    active_protocol = Protocol(dw_active_protocol)

    logging.info(F"Reconnected with share mode: {dw_share_mode.name}")
    logging.info(F"Reconnected with disposition: {dw_initialization.name}")
    logging.info(F"Reconnected with active protocol: {active_protocol.name}")

    return active_protocol


def status(hcard):
    """status():
    """
    hresult, reader, dw_state, dw_protocol, atr = _SCardStatus(hcard)

    if hresult != _SCARD_S_SUCCESS:
        err = F'Unable to get current reader status ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    protocol = Protocol(dw_protocol)
    states = []
    for scard_state in State:
        if dw_state & scard_state:
            states.append(scard_state)

    logging.info(F"Card ATR: {_to_hstr(atr)}")
    logging.info(F"Card connected with active protocol: {protocol.name}")
    logging.info(F"Card in reader: {reader}")
    l = len(states)
    match l:
        case 0:
            logging.info("No card state found")
        case 1:
            logging.info(F"Card state: {states[0].name}")
        case _:
            logging.info(
                F"{l} card states found: {', '.join([state.name for state in states])}")

    return reader, states, protocol, _to_hstr(atr)


def transmit(hcard, protocol: Protocol, command_apdu: CommandApdu) -> ResponseApdu:
    """transmit()
    """
    pio_send_pci = {Protocol.T0: _SCARD_PCI_T0,
                    Protocol.T1: _SCARD_PCI_T1}[protocol]

    hresult, response = _SCardTransmit(
        hcard, pio_send_pci, command_apdu.list())
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to transmit ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    response_apdu = ResponseApdu.from_list(response)
    logging.debug(F"Tx->{command_apdu.str()}")
    logging.debug(F"Rx<-{response_apdu.str()}")

    return response_apdu


def send_apdu(hcard, protocol: Protocol, command_apdu: CommandApdu) -> ResponseApdu:
    """send_apdu()
    """
    match protocol:
        case Protocol.T0:
            match command_apdu.case():
                case CommandCase.Case1:
                    return _send_apdu_T0_case_1(hcard, command_apdu)

                case CommandCase.Case2s:
                    return _send_apdu_T0_case_2s(hcard, command_apdu)

                case CommandCase.Case2e:
                    raise PcscError('Case 2e not yet implemented for T=0')

                case CommandCase.Case3s:
                    return _send_apdu_T0_case_3s(hcard, command_apdu)

                case CommandCase.Case3e:
                    raise PcscError('Case 3e not yet implemented for T=0')

                case CommandCase.Case4s:
                    return _send_apdu_T0_case_4s(hcard, command_apdu)

                case CommandCase.Case4e:
                    raise PcscError('Case 4e not yet implemented for T=0')

        case Protocol.T1:
            return transmit(hcard, protocol, command_apdu)

        case _:
            raise PcscError(
                F'Unsupported protocol: {protocol.name}')


def _send_apdu_T0_case_1(hcard, command_apdu: CommandApdu) -> ResponseApdu:
    """send_apdu_T0_case_1():
    """
    logging.debug('Command APDU Case 1')
    return transmit(hcard, Protocol.T0, command_apdu)


def _send_apdu_T0_case_2s(hcard, command_apdu: CommandApdu) -> ResponseApdu:
    """send_apdu_T0_case_2s():
    """
    logging.debug('Command APDU Case 2S')
    response_apdu = transmit(hcard, Protocol.T0, command_apdu)

    match response_apdu.SW1(), response_apdu.SW2():
        case ('90', '00'):
            # Case 2S.1—Process completed: Ne accepted
            return response_apdu

        case ('67', '00'):
            # Case 2S.2—Process aborted: Ne definitively not accepted
            return response_apdu

        case ('6C', _):
            # Case 2S.3—Process aborted; Ne not accepted, Na indicated
            return transmit(hcard, Protocol.T0, command_apdu.update_Le(response_apdu.SW2()))

        case (sw1, _) if sw1.startswith('9'):
            # Case 2S.4—SW12 = '9XYZ', except for '9000'
            return response_apdu

        case _:
            return response_apdu


def _send_apdu_T0_case_3s(hcard, command_apdu: CommandApdu) -> ResponseApdu:
    logging.debug('Command APDU Case 3s')
    return transmit(hcard, Protocol.T0, command_apdu)


def _send_apdu_T0_case_4s(hcard, command_apdu: CommandApdu) -> ResponseApdu:
    logging.debug('Command APDU Case 4S')
    """send_apdu_T0_case_4s():
    """
    response_apdu = transmit(hcard, Protocol.T0, command_apdu)

    match (response_apdu.SW1(), response_apdu.SW2()):
        case ('64', _) | ('65', _) | ('66', _):
            # Case 4S.1—Process aborted
            return response_apdu

        case ('67', '00') | ('68', _) | ('69', _) | ('6A', _) | ('6C', _):
            # Case 4S.1—Process aborted
            return response_apdu

        case ('6B', '00'):
            # Case 4S.1—Process aborted
            return response_apdu

        case ('6D', '00'):
            # Case 4S.1—Process aborted
            return response_apdu

        case ('6E', '00'):
            # Case 4S.1—Process aborted
            return response_apdu

        case ('6F', '00'):
            # Case 4S.1—Process aborted
            return response_apdu

        case ('90', '00'):
            # Case 4S.2—Process completed
            # Send GET RESPONSE with same Le
            return _send_apdu_T0_case_2s(hcard, _GET_RESPONSE(command_apdu.CLA(), command_apdu.Le()))

        case ('61', sw2):
            # Case 4S.3—Process completed with information added
            Nx = int(sw2, 16)
            if command_apdu.Le() == '00':
                Ne = 0x100
            else:
                Ne = int(command_apdu.Le(), 16)

            Ne = min(Ne, Nx)
            return _send_apdu_T0_case_2s(hcard, _GET_RESPONSE(command_apdu.CLA(), F"{Ne:02X}"))

        case ('62', _) | ('63', _):
            # Case 4S.4—SW12 = '62XY' or '63XY'
            return response_apdu

        case (sw1, _) if sw1.startswith('9'):
            # Case 4S.4—SW12 = '9XYZ', except for '9000'
            return response_apdu

        case _:
            return response_apdu


def get_status_change(hcontext, reader_states=None, timeout=None):
    """get_status_change()
    """
    if reader_states is None:
        readers = list_readers(hcontext)

        reader_states = [(reader, _SCARD_STATE_UNAWARE)
                         for reader in readers]
    old_reader_states = list(
        map(_convert_reader_state_to_scard, reader_states))

    if timeout is None:
        timeout = _INFINITE

    hresult, new_reader_states = _SCardGetStatusChange(
        hcontext, timeout, old_reader_states)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to get new reader states ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    new_reader_states = list(
        map(_convert_reader_state_from_scard, new_reader_states))

    logging.info(F"new reader states: {', '.join(new_reader_states.name)}")
    return new_reader_states


def get_attribute(hcard, attribute: Attribute):
    hresult, value = _SCardGetAttrib(hcard, attribute.value)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to get attribute {attribute} ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)
    if attribute == Attribute.AtrString:
        return _to_hstr(value)
    elif attribute in [Attribute.IfdSerialNo, Attribute.VendorName]:
        return ''.join([chr(i) for i in value])
    else:
        return


def disconnect(hcard, dw_disposition: Disposition):
    """disconnect():
    """
    hresult = _SCardDisconnect(hcard, dw_disposition)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to disconnect ({_SCardGetErrorMessage(hresult)})'
        logging.error(err)
        raise PcscError(err)

    logging.info("Disconnected")


def release_context(hcontext):
    """release_context():
    """
    hresult = _SCardReleaseContext(hcontext)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to release PC/SC context: {_SCardGetErrorMessage(hresult)}'
        logging.error(err)
        raise PcscError(err)

    logging.info("PC/SC context released")

#
# Helper functions
#


# def _compare_reader_states(old_reader_states, new_reader_states):
#     return [new_reader_state for new_reader_state in new_reader_states if new_reader_state[1] & _SCARD_STATE_CHANGED]


def _convert_reader_state_from_scard(reader_state):
    if len(reader_state) == 3:
        reader_state + (_to_hstr(reader_state[2]),)
    else:
        return reader_state


def _convert_reader_state_to_scard(reader_state):
    return reader_state[0:3]
