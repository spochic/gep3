"""apdu.py
"""

# Standard library imports
from enum import Enum
from copy import deepcopy
from array import array

# Third party imports

# Local application imports
from common.hstr import clean as _clean, to_intlist as _to_intlist
from common.intlist import to_hstr as _to_hstr, is_int_list as _is_int_list


# Enum Definitions
class CommandCase(Enum):
    Case1 = 'Case 1'
    Case2S = 'Case 2S'
    Case2E = 'Case 2E'
    Case3S = 'Case 3S'
    Case3E = 'Case 3E'
    Case4S = 'Case 4S'
    Case4E = 'Case 4E'


class CommandField(Enum):
    Header = 'Header'
    Body = 'Body'
    Class = 'Class'
    Instruction = 'Instruction'
    P1 = 'P1'
    P2 = 'P2'
    Lc = 'Lc'
    Data = 'Data'
    Le = 'Le'


class ResponseField(Enum):
    Body = 'Body'
    Trailer = 'Trailer'
    Data = 'Data'
    SW1 = 'SW1'
    SW2 = 'SW2'
    SW12 = 'SW12'


class ResponseProcessingState(Enum):
    Normal = 'Normal procesing'
    Warning = 'Warning processing'
    ExecutionError = 'Execution error'
    CheckingError = 'Checking error'


# Command and Response APDU classes
class CommandApdu:
    # type: ignore
    def __init__(self, CLA: int, INS: int, P1: int, P2: int, data: list[int] = None, Le: int = None):
        if CLA < 0 or CLA > 255:
            raise ValueError(
                F"CommandApdu(): CLA should be [0-255], received: {CLA}")
        elif INS < 0 or INS > 255:
            raise ValueError(
                F"CommandApdu(): INS should be [0-255], received: {INS}")
        elif P1 < 0 or P1 > 255:
            raise ValueError(
                F"CommandApdu(): P1 should be [0-255], received: {P1}")
        elif P2 < 0 or P2 > 255:
            raise ValueError(
                F"CommandApdu(): P2 should be [0-255], received: {P2}")
        elif data is not None:
            if not _is_int_list(data):
                raise ValueError(
                    F"CommandApdu(): data should be list of [0-255], received: {data}")

        self.__content = array('B', [CLA, INS, P1, P2])

        match data, Le:
            case None, None:
                # Case 1
                self.__case = CommandCase.Case1

            case None, _:
                # Case 2
                if Le <= 0:
                    raise ValueError(
                        F"CommandApdu(): Le should be [0-65,536], received: {Le}")
                elif Le < 256:
                    # Case 2S
                    self.__case = CommandCase.Case2S
                    self.__content.append(Le)
                elif Le == 256:
                    # Case 2S
                    self.__case = CommandCase.Case2S
                    self.__content.append(0x00)
                elif Le < 65536:
                    # Case 2E
                    self.__case = CommandCase.Case2E
                    self.__content.extend(int.to_bytes(Le, 3, byteorder='big'))
                elif Le == 65536:
                    # Case 2E
                    self.__case = CommandCase.Case2E
                    self.__content.extend([0x00, 0x00, 0x00])
                else:
                    raise ValueError(
                        F"CommandApdu(): Le should be [0-65,536], received: {Le}")

            case _, None:
                # Case 3
                Lc = len(data)
                if Lc == 0:
                    raise ValueError(
                        F"CommandApdu(): data should not be empty, received: {data}")
                elif Lc < 256:
                    # Case 3S
                    self.__case = CommandCase.Case3S
                    self.__content.append(Lc)
                    self.__content.extend(data)
                elif Lc < 65536:
                    # Case 3E
                    self.__case = CommandCase.Case3E
                    self.__content.extend(int.to_bytes(Lc, 3, byteorder='big'))
                else:
                    raise ValueError(
                        F"CommandApdu(): length of data should be [1-65,535] bytes, received {Lc} bytes ({data})")

            case _, _:
                # Case 4
                Lc = len(data)
                if Le <= 0:
                    raise ValueError(
                        F"CommandApdu(): Le should be [0-65,536], received: {Le}")
                elif Lc == 0:
                    raise ValueError(
                        F"CommandApdu(): data should not be empty, received: {data}")
                elif Lc < 256 and Le <= 256:
                    # Case 4S
                    self.__case = CommandCase.Case4S
                    self.__content.append(Lc)
                    self.__content.extend(data)
                    if Le == 256:
                        self.__content.append(0x00)
                    else:
                        self.__content.append(Le)
                elif Lc < 65536 and Le <= 65536:
                    # Case 4E
                    self.__case = CommandCase.Case4E
                    self.__content.extend(int.to_bytes(Lc, 3, byteorder='big'))
                    self.__content.extend(data)
                    if Le == 65536:
                        self.__content.extend([0x00, 0x00])
                    else:
                        self.__content.extend(
                            int.to_bytes(Le, 2, byteorder='big'))

    @classmethod
    def from_string(cls, apdu_str: str):
        _apdu_list = _to_intlist(
            apdu_str, "CommandApdu.__init__()", "apdu_str")

        apdu_length = len(_apdu_list)

        if apdu_length < 4:
            raise ValueError(
                F'Wrong Command APDU length: expected 4 or more bytes but received {apdu_length}')

        elif apdu_length == 4:
            # Case 1
            return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3])

        elif apdu_length == 5:
            # Case 2S
            return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3], Le=_apdu_list[4])

        elif _apdu_list[4] != 0x00:
            if apdu_length == 5 + _apdu_list[4]:
                # Case 3S
                return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3], data=_apdu_list[5:])
            elif apdu_length == 5 + _apdu_list[4] + 1:
                # Case 4S
                return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3], data=_apdu_list[5:-1], Le=_apdu_list[-1])
            else:
                raise ValueError(
                    F'Wrong Command APDU length: expected {5+_apdu_list[4]} bytes for Case 3s or {5+_apdu_list[4]+1} bytes for Case 4s but received {apdu_length} bytes instead')

        else:
            # Extended length cases
            if apdu_length == 7:
                # Case 2E
                if int.from_bytes(_apdu_list[4:], byteorder='big') == 0:
                    return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3], Le=65536)
                else:
                    return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3], Le=int.from_bytes(_apdu_list[4:], byteorder='big'))

            elif apdu_length == 7 + _apdu_list[5] * 0x0100 + _apdu_list[6]:
                # Case 3E
                return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3], data=_apdu_list[7:])

            elif apdu_length == 7 + _apdu_list[5] * 0x0100 + _apdu_list[6] + 2:
                # Case 4E
                return cls(_apdu_list[0], _apdu_list[1], _apdu_list[2], _apdu_list[3], data=_apdu_list[5:-2], Le=int.from_bytes(_apdu_list[-2:], byteorder='big'))

            else:
                raise ValueError(
                    F'Wrong Command APDU length: expected {7 + _apdu_list[5] * 0x0100 + _apdu_list[6]} bytes for Case 3e or {7 + _apdu_list[5] * 0x0100 + _apdu_list[6] + 2} bytes for Case 4e but received {apdu_length} bytes instead')

    @property
    def case(self) -> CommandCase:
        return self.__case

    @property
    def list(self) -> list[int]:
        return list(self.__content)

    @property
    def string(self) -> str:
        return _to_hstr(self.__content)

    @property
    def array(self):
        return deepcopy(self.__content)

    @property
    def header(self):
        return self.__content[0:4]

    @property
    def body(self):
        return self.__content[4:]

    @property
    def CLA(self):
        return self.__content[0]

    @property
    def INS(self):
        return self.__content[1]

    @property
    def P1(self):
        return self.__content[2]

    @property
    def P2(self):
        return self.__content[3]

    @property
    def Lc(self):
        match self.__case:
            case CommandCase.Case1 | CommandCase.Case2S | CommandCase.Case2E:
                raise ValueError(
                    F'Command APDU has no Lc field ({self.case.value})')
            case CommandCase.Case3S | CommandCase.Case4S | CommandCase.Case3E | CommandCase.Case4E:
                return len(self.data)

    @property
    def data(self):
        match self.case:
            case CommandCase.Case1 | CommandCase.Case2S | CommandCase.Case2E:
                raise ValueError(
                    F'Command APDU has no Data field ({self.case.value})')
            case CommandCase.Case3S:
                return self.__content[5:]
            case CommandCase.Case4S:
                return self.__content[5:-1]
            case CommandCase.Case3E:
                return self.__content[7:]
            case CommandCase.Case4E:
                return self.__content[7:-2]

    @property
    def Le(self):
        match self.case:
            case CommandCase.Case1 | CommandCase.Case3S | CommandCase.Case3E:
                raise ValueError(
                    F'Command APDU has no Le field ({self.case.value})')
            case CommandCase.Case2S | CommandCase.Case4S:
                if self.__content[-1] == 0x00:
                    return 256
                else:
                    return self.__content[-1]
            case CommandCase.Case2E | CommandCase.Case4E:
                if list(self.__content[-2:]) == [0x00, 0x00]:
                    return 65536
                else:
                    return int.from_bytes(self.__content[-2:], byteorder='big')

    def __str__(self):
        str = F"{self.__class__.__name__} ({self.case.value}): CLA={self.CLA:02X}, INS={self.INS:02X}, P1={self.P1:02X}, P2={self.P2:02X}"

        match self.case:
            case CommandCase.Case1:
                return str
            case CommandCase.Case2S:
                return str + F", Le={self.Le:02X}"
            case CommandCase.Case2E:
                return str + F", Le={self.Le:06X}"
            case CommandCase.Case3S:
                return str + F", Lc={self.Lc:02X}, DATA={_to_hstr(self.data)}"
            case CommandCase.Case3E:
                return str + F", Lc={self.Lc:06X}, DATA={_to_hstr(self.data)}"
            case CommandCase.Case4S:
                return str + F", Lc={self.Lc:02X}, DATA={_to_hstr(self.data)}, Le={self.Le:02X}"
            case CommandCase.Case4E:
                return str + F", Lc={self.Lc:06X}, DATA={_to_hstr(self.data)}, Le={self.Le:04X}"

    def update_Le(self, Le: str):
        match self.case:
            case CommandCase.Case1 | CommandCase.Case3S | CommandCase.Case3E:
                raise ValueError(
                    F'Command APDU has no Le field ({self.case.value})')

            case CommandCase.Case2S | CommandCase.Case2E:
                return CommandApdu(self.CLA, self.INS, self.P1, self.P2, Le=int(Le, 16))

            case CommandCase.Case4S | CommandCase.Case4E:
                return CommandApdu(self.CLA, self.INS, self.P1, self.P2, data=list(self.data), Le=int(Le, 16))

    def with_updated_Le(self, Le: int):
        match self.case:
            case CommandCase.Case1 | CommandCase.Case3S | CommandCase.Case3E:
                raise ValueError(
                    F'Command APDU has no Le field ({self.case.value})')

            case CommandCase.Case2S | CommandCase.Case2E:
                return CommandApdu(self.CLA, self.INS, self.P1, self.P2, Le=Le)

            case  CommandCase.Case4S | CommandCase.Case4E:
                return CommandApdu(self.CLA, self.INS, self.P1, self.P2, data=list(self.data), Le=Le)


class StatusBytes:
    def __init__(self, sw12: str):
        self.__list = _to_intlist(sw12, "StatusBytes.__init__()", "sw12")
        if len(self.__list) != 2:
            raise ValueError(F"Expected 2 bytes, received: {sw12}")

        first_digit = self.__list[0] >> 4
        if first_digit not in [0x6, 0x9]:
            raise ValueError(F"Expected 6XXX or 9XXX value, received: {sw12}")

        if self.__list[0] == 0x60:
            raise ValueError(F"60XX in valid, received: {sw12}")

        match self.__list:
            case [0x90, 0x00]:
                self.__state = ResponseProcessingState.Normal
                self.__meaning = 'No further qualification'
            case [0x61, _]:
                self.__state = ResponseProcessingState.Normal
                self.__meaning = 'SW2 encodes the number of data bytes still available'
            case [0x62, sw2]:
                self.__state = ResponseProcessingState.Warning
                self.__meaning = {0x00: 'No information given',
                                  0x81: 'Part of returned data may be corrupted',
                                  0x82: 'End of file or record reached before reading Ne bytes',
                                  0x83: 'Selected file deactivated',
                                  0x84: 'File control information not formatted according to ISO7816-4 5.3.3',
                                  0x85: 'Selected file in termination state',
                                  0x86: 'No input data available from a sensor on the card'}.get(sw2, 'State of non-volatile memory is unchanged')
            case [0x63, sw2]:
                self.__state = ResponseProcessingState.Warning
                self.__meaning = {0x00: 'No information given',
                                  0x81: 'File filled up by the last '}.get(sw2, 'State of non-volatile memory has changed(further qualification in SW2)')
            case [0x64, sw2]:
                self.__state = ResponseProcessingState.ExecutionError
                self.__meaning = {0x00: 'Execution error',
                                  0x01: 'Immediate response required by the card'}.get(sw2, 'State of non-volatile memory is unchanged (further qualification in SW2)')
            case [0x65, sw2]:
                self.__state = ResponseProcessingState.ExecutionError
                self.__meaning = {0x00: 'No information given',
                                  0x81: 'Memory failure'}.get(sw2, 'State of non-volatile memory has changed (further qualification in SW2)')
            case [0x66, _]:
                self.__state = ResponseProcessingState.ExecutionError
                self.__meaning = 'Security-related issues'
            case [0x67, 0x00]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = 'Wrong length; no further indication'
            case [0x68, sw2]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = {0x00: 'No information given',
                                  0x81: 'Logical channel not supported',
                                  0x82: 'Secure messaging not supported',
                                  0x83: 'Last command of the chain expected',
                                  0x84: 'Command chaining not supported'}.get(sw2, 'Functions in CLA not supported (further qualification in SW2)')
            case [0x69, sw2]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = {0x00: 'No information given',
                                  0x81: 'Command incompatible with file structure',
                                  0x82: 'Security status not satisfied',
                                  0x83: 'Authentication method blocked',
                                  0x84: 'Reference data not usable',
                                  0x85: 'Conditions of use not satisfied',
                                  0x86: 'Command not allowed (no current EF)',
                                  0x87: 'Expected secure messaging data objects missing',
                                  0x88: 'Incorrect secure messaging data objects'}.get(sw2, 'Command not allowed (further qualification in SW2)')
            case [0x6A, _]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = 'Wrong parameters P1-P2 (further qualification in SW2)'
            case [0x6B, 0x00]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = 'Wrong parameters P1-P2'
            case [0x6C, _]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = 'Wrong Le field; SW2 encodes the exact number of available data bytes'
            case [0x6D, 0x00]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = 'Instruction code not supported or invalid'
            case [0x6E, 0x00]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = 'Class not supported'
            case [0x6F, 0x00]:
                self.__state = ResponseProcessingState.CheckingError
                self.__meaning = 'No precise diagnosis'

    @property
    def state(self):
        return self.__state

    @property
    def meaning(self):
        return self.__meaning


class ResponseApdu:
    def __init__(self, apdu_str: str):
        self.__list = _to_intlist(
            apdu_str, "ResponseApdu.__init__()", "apdu_str")

    @classmethod
    def from_list(cls, response: list[int]):
        return cls(_to_hstr(response))

    @property
    def list(self):
        return self.__list

    @property
    def string(self):
        return _to_hstr(self.__list)

    def get_field(self, field: ResponseField) -> str:
        match field:
            case ResponseField.Trailer | ResponseField.SW12:
                return _to_hstr(self.__list[-2:])

            case ResponseField.SW1:
                return F"{self.__list[-2]:02X}"

            case ResponseField.SW2:
                return F"{self.__list[-1]:02X}"

            case ResponseField.Body | ResponseField.Data:
                if len(self.__list) > 2:
                    return _to_hstr(self.__list[0:-2])
                else:
                    raise ValueError(
                        'Wrong Response APDU field: no response body')

    @property
    def data(self) -> str:
        return self.get_field(ResponseField.Data)

    @property
    def SW12(self) -> str:
        return self.get_field(ResponseField.SW12)

    @property
    def SW1(self) -> str:
        return self.get_field(ResponseField.SW1)

    @property
    def SW2(self) -> str:
        return self.get_field(ResponseField.SW2)

    @property
    def StatusBytes(self) -> StatusBytes:
        return StatusBytes(self.get_field(ResponseField.SW12))

    def __str__(self):
        return _to_hstr(self.__list)


#
# Helper functions
#
def _Lc(data: list[int]):
    Lc = len(data)
    if Lc < 256:
        return [Lc]

    if Lc < 65536:
        return [0x00, Lc >> 8, Lc & 0x00FF]

    raise ValueError(F'Data length should be <65,536: actual length = {Lc}')


def _dict_to_string(apdu: dict):
    # If 'apdu' includes a header, it will be used directly. If not, the header will be constructed with CLA, INS, P1, and P2
    if CommandField.Header in apdu:
        header = apdu[CommandField.Header]
    else:
        header = apdu[CommandField.Class] + apdu[CommandField.Instruction] + \
            apdu[CommandField.P1] + apdu[CommandField.P2]

    # If 'apdu' includes a body, it will be used directly. If not, the body will be constructed with the optional DATA and Le fields
    body = ''
    if CommandField.Body in apdu:
        body = apdu[CommandField.Body]
    else:
        if CommandField.Data in apdu:
            _DATA = apdu[CommandField.Data]
            body = F"{''.join([F'{l:02X}' for l in _Lc(_to_intlist(_DATA))])}{_DATA}"

        if CommandField.Le in apdu:
            body += apdu[CommandField.Le]

    return header + body


def _byte_to_string(byte, command_name='()', byte_name='') -> str:
    if (byte < 0x00) or (byte > 0xFF):
        raise ValueError(
            F'{command_name}: {byte_name} out of bound, received {byte:X}')
    else:
        return F"{byte:02X}"
