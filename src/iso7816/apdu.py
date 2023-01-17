"""apdu.py
"""

# Standard library imports
from enum import Enum

# Third party imports

# Local application imports
from common.hstr import clean as _clean, to_intlist as _to_intlist
from common.intlist import to_hstr as _to_hstr

# Enum Definitions


class CommandCase(Enum):
    Case1 = 'Case 1'
    Case2s = 'Case 2s'
    Case2e = 'Case 2e'
    Case3s = 'Case 3s'
    Case3e = 'Case 3e'
    Case4s = 'Case 4s'
    Case4e = 'Case 4e'


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
    def __init__(self, apdu_str: str):
        self.__list = _to_intlist(
            apdu_str, "CommandApdu.__init__()", "apdu_str")

        apdu_length = len(self.__list)

        if apdu_length < 4:
            raise ValueError(
                F'Wrong Command APDU length: expected 4 or more bytes but received {apdu_length}')

        elif apdu_length == 4:
            self.__case = CommandCase.Case1

        elif apdu_length == 5:
            self.__case = CommandCase.Case2s

        elif self.__list[4] != 0x00:
            if apdu_length == 5 + self.__list[4]:
                self.__case = CommandCase.Case3s
            elif apdu_length == 5 + self.__list[4] + 1:
                self.__case = CommandCase.Case4s
            else:
                raise ValueError(
                    F'Wrong Command APDU length: expected {5+self.__list[4]} bytes for Case 3s or {5+self.__list[4]+1} bytes for Case 4s but received {apdu_length} bytes instead')

        else:
            # Extended length cases
            if apdu_length == 7:
                self.__case = CommandCase.Case2e

            elif apdu_length == 7 + self.__list[5] * 0x0100 + self.__list[6]:
                self.__case = CommandCase.Case3e

            elif apdu_length == 7 + self.__list[5] * 0x0100 + self.__list[6] + 2:
                self.__case = CommandCase.Case4e

            else:
                raise ValueError(
                    F'Wrong Command APDU length: expected {7 + self.__list[5] * 0x0100 + self.__list[6]} bytes for Case 3e or {7 + self.__list[5] * 0x0100 + self.__list[6] + 2} bytes for Case 4e but received {apdu_length} bytes instead')

    @classmethod
    def from_dict(cls, apdu: dict):
        # If 'apdu' includes a header, it will be used directly. If not, the header will be constructed with CLA, INS, P1, and P2
        if CommandField.Header in apdu:
            apdu_str = _clean(
                apdu[CommandField.Header], 'CommandApdu.from_dict()', 'apdu[CommandField.Header]')
        else:
            apdu_str = F"{_clean(apdu[CommandField.Class], 'CommandApdu.from_dict()', 'apdu[CommandField.Class]')}{_clean(apdu[CommandField.Instruction], 'CommandApdu.from_dict()', 'apdu[CommandField.Instruction]')}{_clean(apdu[CommandField.P1], 'CommandApdu.from_dict()', 'apdu[CommandField.P1]')}{_clean(apdu[CommandField.P2], 'CommandApdu.from_dict()', 'apdu[CommandField.P2]')}"

        # If 'apdu' includes a body, it will be used directly. If not, the body will be constructed with the optional DATA and Le fields
        if CommandField.Body in apdu:
            apdu_str += _clean(apdu[CommandField.Body],
                               'CommandApdu.from_dict()', 'apdu[CommandField.Body]')
        else:

            if CommandField.Data in apdu:
                _DATA = _clean(
                    apdu[CommandField.Data], 'CommandApdu.from_dict()', 'apdu[CommandField.Data]')
                apdu_str += F"{''.join([F'{l:02X}' for l in _Lc(_to_intlist(_DATA))])}{_DATA}"

            if CommandField.Le in apdu:
                apdu_str += _clean(apdu[CommandField.Le],
                                   "CommandApdu.__init__()", "apdu[CommandField.Le]")

        return cls(apdu_str)

    def list(self):
        return self.__list

    def str(self):
        return _to_hstr(self.__list)

    def get_field(self, field: CommandField):
        match field:
            case CommandField.Header:
                return _to_hstr(self.__list[0:4])

            case CommandField.Body:
                return _to_hstr(self.__list[4:])

            case CommandField.Class:
                return F"{self.__list[0]:02X}"

            case CommandField.Instruction:
                return F"{self.__list[1]:02X}"

            case CommandField.P1:
                return F"{self.__list[2]:02X}"

            case CommandField.P2:
                return F"{self.__list[3]:02X}"

            case CommandField.Lc:
                match self.__case:
                    case CommandCase.Case1 | CommandCase.Case2s | CommandCase.Case2e:
                        raise ValueError(
                            F'Wrong Command APDU field: {self.__case} has no Lc field')
                    case CommandCase.Case3s | CommandCase.Case4s:
                        return F"{self.__list[4]:02X}"
                    case CommandCase.Case3e | CommandCase.Case4e:
                        return _to_hstr(self.__list[4:7])

            case CommandField.Data:
                match self.__case:
                    case CommandCase.Case1 | CommandCase.Case2s | CommandCase.Case2e:
                        raise ValueError(
                            F'Wrong Command APDU field: {self.__case} has no Data field')
                    case CommandCase.Case3s:
                        return _to_hstr(self.__list[5:])
                    case CommandCase.Case4s:
                        return _to_hstr(self.__list[5:-1])
                    case CommandCase.Case3e:
                        return _to_hstr(self.__list[7:])
                    case CommandCase.Case4e:
                        return _to_hstr(self.__list[7:-2])

            case CommandField.Le:
                match self.__case:
                    case CommandCase.Case1 | CommandCase.Case3s | CommandCase.Case3e:
                        raise ValueError(
                            F'Wrong Command APDU field: {self.__case} has no Le field')
                    case CommandCase.Case2s | CommandCase.Case4s:
                        return F"{self.__list[-1]:02X}"
                    case CommandCase.Case2e | CommandCase.Case4e:
                        return _to_hstr(self.__list[-2:])

    def CLA(self):
        return self.get_field(CommandField.Class)

    def INS(self):
        return self.get_field(CommandField.Instruction)

    def P1(self):
        return self.get_field(CommandField.P1)

    def P2(self):
        return self.get_field(CommandField.P2)

    def Le(self):
        return self.get_field(CommandField.Le)

    def case(self):
        return self.__case

    def __str__(self):
        str = F"Command APDU ({self.__case.value}): CLA={self.CLA()}, INS={self.INS()}, P1={self.P1()}, P2={self.P2()}"

        match self.__case:
            case CommandCase.Case1:
                return str
            case CommandCase.Case2s | CommandCase.Case2e:
                return str + F", Le={self.Le()}"
            case CommandCase.Case3s | CommandCase.Case3e:
                return str + F", Lc={self.Lc()}, DATA={self.DATA()}"
            case CommandCase.Case4s | CommandCase.Case4e:
                return str + F", Lc={self.Lc()}, DATA={self.DATA()}, Le={self.Le()}"

    def update_Le(self, Le: str):
        match self.__case:
            case CommandCase.Case1 | CommandCase.Case3s | CommandCase.Case3e:
                raise ValueError(
                    F'Wrong Command APDU field: {self.__case} has no Le field')

            case CommandCase.Case2s | CommandCase.Case2e:
                return CommandApdu.from_dict({CommandField.Header: self.get_field(CommandField.Header),
                                              CommandField.Le: Le})

            case CommandCase.Case4s | CommandCase.Case4e:
                return CommandApdu.from_dict({CommandField.Header: self.get_field(CommandField.Header),
                                              CommandField.Data: self.get_field(CommandField.Data),
                                              CommandField.Le: Le})


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

    def state(self):
        return self.__state

    def meaning(self):
        return self.__meaning


class ResponseApdu:
    def __init__(self, apdu_str: str):
        self.__list = _to_intlist(
            apdu_str, "ResponseApdu.__init__()", "apdu_str")

    @classmethod
    def from_list(cls, response: list[int]):
        return cls(_to_hstr(response))

    def list(self):
        return self.__list

    def str(self):
        return _to_hstr(self.__list)

    def get_field(self, field: ResponseField):
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

    def data(self):
        return self.get_field(ResponseField.Data)

    def SW12(self):
        return self.get_field(ResponseField.SW12)

    def SW1(self):
        return self.get_field(ResponseField.SW1)

    def SW2(self):
        return self.get_field(ResponseField.SW2)

    def StatusBytes(self):
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
