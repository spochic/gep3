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
        logging.debug(err)
        raise PcscError(err)

    logging.debug(F"PC/SC context established with scope={dw_scope}")
    return hcontext


def list_readers(hcontext, readergroups=None):
    """list_readers():
    """
    if readergroups is None:
        readergroups = []

    hresult, readers = _SCardListReaders(hcontext, readergroups)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to list readers ({_SCardGetErrorMessage(hresult)})'
        logging.debug(err)
        raise PcscError(err)

    logging.debug(F"Readers listed: {', '.join(readers)}")
    return readers


def list_readers_with_serialno(hcontext, readergroups=None):
    """list_readers_with_serialno():
    """
    if readergroups is None:
        readergroups = []

    readers = list_readers(hcontext, readergroups)
    serial_nos = []
    for r in readers:
        hcard, _ = connect(hcontext, r, ShareMode.Direct, Protocol.T0orT1)
        serial_nos.append(get_attribute(hcard, Attribute.IfdSerialNo))
        disconnect(hcard, Disposition.UnpowerCard)

    logging.debug(
        F"Readers listed: {', '.join([F'{r} ({s})' for r,s in zip(readers, serial_nos)])}")
    return readers, serial_nos


def connect(hcontext, reader, dw_share_mode: ShareMode, dw_preferred_protocols: Protocol):
    """connect():
    """
    hresult, hcard, dw_active_protocol = _SCardConnect(
        hcontext, reader, dw_share_mode, dw_preferred_protocols)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Unable to connect ({_SCardGetErrorMessage(hresult)})'
        logging.debug(err)
        raise PcscError(err)

    protocol = Protocol(dw_active_protocol)
    logging.debug(F"Connected with mode={dw_share_mode}, protocol={protocol}")
    return hcard, protocol


def reconnect(hcard, dw_share_mode: ShareMode, dw_preferred_protocols: Protocol, dw_initialization: Disposition):
    """reconnect():
    """
    hresult, dw_active_protocol = _SCardReconnect(
        hcard, dw_share_mode, dw_preferred_protocols, dw_initialization)

    if hresult != _SCARD_S_SUCCESS:
        err = F'Unable to reconnect ({_SCardGetErrorMessage(hresult)})'
        logging.debug(err)
        raise PcscError(err)

    active_protocol = Protocol(dw_active_protocol)
    logging.debug(
        F"Reconnected with mode={dw_share_mode}, disposition={dw_initialization}, protocol={active_protocol}")
    return active_protocol


def status(hcard):
    """status():
    """
    hresult, reader, dw_state, dw_protocol, atr = _SCardStatus(hcard)

    if hresult != _SCARD_S_SUCCESS:
        err = F'Unable to get current reader status ({_SCardGetErrorMessage(hresult)})'
        logging.debug(err)
        raise PcscError(err)

    protocol = Protocol(dw_protocol)
    state = []
    for scard_state in State:
        if dw_state & scard_state:
            state.append(scard_state)
    logging.debug(
        F"Card status: reader='{reader}', state={state}, protocol={protocol}, ATR={_to_hstr(atr)}")
    return reader, state, protocol, _to_hstr(atr)


def transmit(hcard, protocol: Protocol, apdu: str):
    """transmit()
    """
    pio_send_pci = {Protocol.T0: _SCARD_PCI_T0,
                    Protocol.T1: _SCARD_PCI_T1}[protocol]

    apdu_bytes = _to_intlist(apdu)

    hresult, response_bytes = _SCardTransmit(hcard, pio_send_pci, apdu_bytes)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to transmit ({_SCardGetErrorMessage(hresult)})'
        logging.debug(err)
        raise PcscError(err)

    response = _to_hstr(response_bytes)
    data = response[0:-4]
    SW1 = response[-4:-2]
    SW2 = response[-2:]
    logging.debug(F"Tx->{apdu}")
    logging.debug(F"Rx<-{data}{SW1}{SW2}")

    return data, SW1, SW2


def send_apdu(hcard, protocol: Protocol, apdu: dict):
    """send_apdu()
    """
    # Extracting APDU header, data, length field from apdu dictionary
    if 'header' in apdu:
        header = _clean(apdu['header'])
    else:
        CLA = _clean(apdu['CLA'])
        INS = _clean(apdu['INS'])
        P1 = _clean(apdu['P1'])
        P2 = _clean(apdu['P2'])
        header = CLA + INS + P1 + P2

    data = apdu.get('data', None)
    Le = apdu.get('Le', None)

    if protocol not in Protocol:
        raise PcscError(F'Unsupported protocol: {protocol}')

    if data is None:
        # Case 1
        if Le is None:
            logging.debug("Case 1")
            if protocol == Protocol.T0:
                return _send_apdu_T0_case_1(hcard, header)
            if protocol == Protocol.T1:
                return transmit(hcard, protocol, header)
        # Case 2S
        logging.debug("Case 2S")
        Le = _clean(Le, 'send_apdu()', 'Le')
        if len(Le) == 2:
            if protocol == Protocol.T0:
                return _send_apdu_T0_case_2s(hcard, header, Le)
            if protocol == Protocol.T1:
                return transmit(hcard, protocol, header + Le)
        # Case 2E
        logging.debug("Case 2E")
        if len(Le) == 6:
            if protocol == Protocol.T0:
                raise PcscError('Unsupported case 2E with protocol T=0')
            if protocol == Protocol.T1:
                return transmit(hcard, protocol, header + Le)

    data = _clean(data, 'send_apdu()', 'data')
    Lc = len(data)//2
    if Le is None:
        # Case 3S
        logging.debug("Case 3S")
        if Lc < 256:
            Lc = F"{Lc:02X}"
            if protocol == Protocol.T0:
                return _send_apdu_T0_case_3s(hcard, header, Lc, data)
            if protocol == Protocol.T1:
                return transmit(hcard, protocol, header + Lc + data)
        # Case 3E
        logging.debug("Case 3E")
        if Lc < 65536:
            Lc = F"00{Lc:04X}"
            if protocol == Protocol.T0:
                raise PcscError('Unsupported case 3E with protocol T=0')
            if protocol == Protocol.T1:
                return transmit(hcard, protocol, header + Lc + data)
        # Data field too long
        else:
            raise PcscError(F"Data field too long: {Lc:X}")

    # Case 4S
    logging.debug("Case 4S")
    if Lc < 256 and len(Le) == 2:
        if protocol == Protocol.T0:
            return _send_apdu_T0_case_4s(hcard, header, F"{Lc:02X}", data, Le)
        if protocol == Protocol.T1:
            return transmit(hcard, protocol, header + F"{Lc:02X}" + data + Le)
    # Case 4E
    logging.debug("Case 4E")
    if Lc < 65536 and len(Le) == 6:
        if protocol == Protocol.T0:
            raise PcscError('Unsupported case 4E with protocol T=0')
        if protocol == Protocol.T1:
            return transmit(hcard, protocol, header + F"00{Lc:04X}" + data + Le)

    raise PcscError(
        F'Unsupported case with short and extended lengths: Lc = {Lc:X}, Le = {Le}')


def _send_apdu_T0_case_1(hcard, header: str):
    """send_apdu_T0_case_1():
    """
    return transmit(hcard, Protocol.T0, header)


def _send_apdu_T0_case_2s(hcard, header: str, Le: str):
    """send_apdu_T0_case_2s():
    """
    # Short Le field
    if len(Le) == 2:
        pass
    # Wrong Le field
    else:
        raise PcscError(F'Wrong Le value: {Le}')

    data, SW1, SW2 = transmit(hcard, Protocol.T0, header + Le)
    if SW1+SW2 == '6B00':
        raise PcscError(
            'Checking error: Wrong parameters P1-P2 (6B00)')
    if SW1+SW2 == '6D00':
        raise PcscError(
            'Checking error: Instruction code not supported or invalid (6D00)')
    if SW1+SW2 == '6E00':
        raise PcscError(
            'Checking error: Class not supported (6E00)')
    if SW1+SW2 == '6F00':
        raise PcscError(
            'Checking error: No precise diagnostis (6F00)')

    # Case 2S.1—Process completed: Ne accepted
    if SW1+SW2 == '9000':
        return data, SW1, SW2

    # Case 2S.2—Process aborted: Ne definitively not accepted
    if SW1+SW2 == '6700':
        raise PcscError(
            'Error—Process aborted: Ne definitively not accepted (6700)')

    # Case 2S.3—Process aborted; Ne not accepted, Na indicated
    if SW1 == '6C':
        return transmit(hcard, Protocol.T0, header + SW2)

    # Case 2S.4—SW12 = '9XYZ', except for '9000'
    if SW1.startswith('9'):
        return data, SW1, SW2

    raise PcscError(F'Unknown command case (data={data}, SW12={SW1}{SW2})')


def _send_apdu_T0_case_3s(hcard, header: str, Lc: str, data: str):
    """send_apdu_T0_case_3s():
    """
    # Short Lc field
    if len(Lc) == 2:
        pass
    # Data field too long
    else:
        raise PcscError(F"Data field too long: {Lc}")

    return transmit(hcard, Protocol.T0, header + Lc + data)


def _send_apdu_T0_case_4s(hcard, header: str, Lc: str, data: str, Le: str):
    """send_apdu_T0_case_4s():
    """
    # Short Lc field
    if len(Lc) == 2:
        pass
    # Data field too long
    else:
        raise PcscError(F"Data field too long: {Lc}")

    # Short Le field
    if len(Le) == 2:
        pass
    # Wrong Le field
    else:
        raise PcscError(F'Wrong Le value: {Le}')

    data, SW1, SW2 = transmit(hcard, Protocol.T0, header + Lc + data + Le)
    # Case 4S.1—Process aborted
    if SW1[0] == '6' and SW1[1] in '0456789ABCDEF':
        raise PcscError(
            F'Error—Process aborted (data={data}, SW12={SW1}{SW2})')
    # Case 4S.2—Process completed
    if SW1+SW2 == '9000':
        # Send GET RESPONSE
        return _send_apdu_T0_case_2s(hcard, Protocol.T0, header[0:2] + 'C00000', Le)
    # Case 4S.3—Process completed with information added
    if SW1 == '61':
        if Le == '00':
            Ne = '100'
        else:
            Ne = Le
        return _send_apdu_T0_case_2s(hcard, Protocol.T0, header[0:2] + 'C00000', _min(Ne, SW2))
    # Case 4S.4—SW12 = '62XY', or '63XY', or '9XYZ', except for '9000'
    if SW1.startswith('9') or SW1 in ['62', '63']:
        return data, SW1, SW2

    raise PcscError(F'Unknown command case (data={data}, SW12={SW1}{SW2})')


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
        logging.debug(err)
        raise PcscError(err)

    new_reader_states = list(
        map(_convert_reader_state_from_scard, new_reader_states))

    logging.debug(F"new reader states: {', '.join(new_reader_states)}")
    return new_reader_states


def get_attribute(hcard, attribute: Attribute):
    hresult, value = _SCardGetAttrib(hcard, attribute.value)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to get attribute {attribute} ({_SCardGetErrorMessage(hresult)})'
        logging.debug(err)
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
        logging.debug(err)
        raise PcscError(err)

    logging.debug("Disconnected")


def release_context(hcontext):
    """release_context():
    """
    hresult = _SCardReleaseContext(hcontext)
    if hresult != _SCARD_S_SUCCESS:
        err = F'Failed to release PC/SC context: {_SCardGetErrorMessage(hresult)}'
        logging.debug(err)
        raise PcscError(err)

    logging.debug("PC/SC context released")

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
