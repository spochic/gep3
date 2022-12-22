"""iso7816.py
"""

# Standard library imports
from enum import Enum

# Third party imports

# Local application imports
from .hstr import clean as _clean, to_intlist as _to_intlist
from .intlist import to_hstr as _to_hstr

# Definitions


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

    def __str__(self):
        return _to_hstr(self.__list)


#
# Commands for interchange
#

def GET_RESPONSE(CLA: str, Le: str):
    return CommandApdu.from_dict({CommandField.Class: CLA, CommandField.Instruction: 'C0', CommandField.P1: '00', CommandField.P2: '00', CommandField.Le: Le})


def SELECT(CLA: str, P1: str, P2: str, Identifier: str = None, Le: str = None):
    apdu_dict = {CommandField.Class: CLA, CommandField.Instruction: 'A4',
                 CommandField.P1: P1, CommandField.P2: P2}

    if Identifier is not None:
        apdu_dict[CommandField.Data] = Identifier

    if Le is not None:
        apdu_dict[CommandField.Le] = Le

    return CommandApdu.from_dict(apdu_dict)


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
