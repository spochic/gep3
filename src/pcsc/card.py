"""card.py: Exception-less version of pcsc.scard
"""

# Standard library imports

# Third party imports

# Local application imports
from pcsc.scard import Scope, ShareMode, Protocol, Disposition, State, Attribute, PcscError, CommandApdu, ResponseApdu
import pcsc.scard as _scard


# Functions definitions
def establish_context(dw_scope: Scope):
    """establish_context():
    """
    try:
        return _scard.establish_context(dw_scope), None
    except PcscError as e:
        return None, str(e)


def list_readers(hcontext, readergroups=None):
    """list_readers():
    """
    try:
        return _scard.list_readers(hcontext, readergroups), None
    except PcscError as e:
        return None, str(e)


def list_readers_serialno(hcontext, readers):
    """list_readers_serialno():
    """
    try:
        return _scard.list_readers_serialno(hcontext, readers), None
    except PcscError as e:
        return None, str(e)


def connect(hcontext, reader, dw_share_mode: ShareMode, dw_preferred_protocols: Protocol):
    """connect():
    """
    try:
        return _scard.connect(hcontext, reader, dw_share_mode, dw_preferred_protocols), None
    except PcscError as e:
        return None, str(e)


def reconnect(hcard, dw_share_mode: ShareMode, dw_preferred_protocols: Protocol, dw_initialization: Disposition):
    """reconnect():
    """
    try:
        return _scard.reconnect(hcard, dw_share_mode, dw_preferred_protocols, dw_initialization), None
    except PcscError as e:
        return None, str(e)


def status(hcard):
    """status():
    """
    try:
        return _scard.status(hcard), None
    except PcscError as e:
        return None, str(e)


def transmit(hcard, protocol: Protocol, command_apdu: CommandApdu) -> ResponseApdu:
    """transmit()
    """
    try:
        return _scard.transmit(hcard, protocol, command_apdu), None
    except PcscError as e:
        return None, str(e)


def send_apdu(hcard, protocol: Protocol, command_apdu: CommandApdu) -> ResponseApdu:
    """send_apdu()
    """
    try:
        return _scard.send_apdu(hcard, protocol, command_apdu), None
    except PcscError as e:
        return None, str(e)


def get_status_change(hcontext, reader_states=None, timeout=None):
    """get_status_change()
    """
    try:
        return _scard.get_status_change(hcontext, reader_states, timeout), None
    except PcscError as e:
        return None, str(e)


def get_attribute(hcard, attribute: Attribute):
    """get_attribute()
    """
    try:
        return _scard.get_attribute(hcard, attribute), None
    except PcscError as e:
        return None, str(e)


def disconnect(hcard, dw_disposition: Disposition):
    """disconnect():
    """
    try:
        return _scard.disconnect(hcard, dw_disposition)
    except PcscError as e:
        return str(e)


def release_context(hcontext):
    """release_context():
    """
    try:
        return _scard.release_context(hcontext), None
    except PcscError as e:
        return None, str(e)


#
# Helper functions
#
