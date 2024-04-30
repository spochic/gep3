"""apdu.py
"""

# Standard library imports
from __future__ import annotations
from enum import StrEnum
from typing import Optional

# Third party imports

# Local application imports
from common.binary import ByteString
from .encodings import Lc, Le


# Enum Definitions
class CommandCase(StrEnum):
    Case1 = 'Case 1'
    Case2S = 'Case 2S'
    Case2E = 'Case 2E'
    Case3S = 'Case 3S'
    Case3E = 'Case 3E'
    Case4S = 'Case 4S'
    Case4E = 'Case 4E'


class CommandField(StrEnum):
    Header = 'Header'
    Body = 'Body'
    Class = 'Class'
    Instruction = 'Instruction'
    P1 = 'P1'
    P2 = 'P2'
    Lc = 'Lc'
    Data = 'Data'
    Le = 'Le'


class ResponseProcessingState(StrEnum):
    Normal = 'Normal procesing'
    Warning = 'Warning processing'
    ExecutionError = 'Execution error'
    CheckingError = 'Checking error'


# Command and Response APDU classes
class CommandApdu(ByteString):
    def __init__(self, CLA: ByteString, INS: ByteString, P1: ByteString, P2: ByteString, data_field: Optional[ByteString], Ne: Optional[int]):
        for param in ["CLA", "INS", "P1", "P2"]:
            if len(locals()[param]) != 1:
                raise ValueError(
                    F"{param} should be 1 byte, received: {locals()[param]}")

        match data_field, Ne:
            case None, None:
                # Case 1
                super().__init__(str(CLA + INS + P1 + P2))
                self.__case = CommandCase.Case1

            case None, int():
                # Case 2
                if len(Le(Ne)) == 1:
                    # Case 2S
                    super().__init__(str(CLA + INS + P1 + P2 + Le(Ne)))
                    self.__case = CommandCase.Case2S
                else:
                    # Case 2E
                    super().__init__(str(CLA + INS + P1 + P2 + Le(Ne)))
                    self.__case = CommandCase.Case2E

            case ByteString(), None:
                # Case 3
                if len(Lc(data_field)) == 1:
                    # Case 3S
                    super().__init__(str(CLA + INS + P1 + P2 + Lc(data_field) + data_field))
                    self.__case = CommandCase.Case3S
                else:
                    # Case 3E
                    super().__init__(str(CLA + INS + P1 + P2 + Lc(data_field) + data_field))
                    self.__case = CommandCase.Case3E

            case ByteString(), int():
                # Case 4
                if len(Le(Ne)) == 1:
                    # Case 4S
                    super().__init__(str(CLA + INS + P1 + P2 + Lc(data_field) + data_field + Le(Ne)))
                    self.__case = CommandCase.Case4S
                else:
                    # Case 4E
                    super().__init__(str(CLA + INS + P1 + P2 + Lc(data_field) + data_field + Le(Ne)))
                    self.__case = CommandCase.Case4E

            case _, _:
                raise ValueError(
                    F"Received wrong data_field ({data_field}) and/or Ne ({Ne})")

    @property
    def case(self) -> CommandCase:
        return self.__case

    @property
    def header(self) -> ByteString:
        return self[0:4]

    @property
    def body(self) -> ByteString:
        return self[4:]

    @property
    def CLA(self) -> ByteString:
        return self[0]

    @property
    def INS(self) -> ByteString:
        return self[1]

    @property
    def P1(self) -> ByteString:
        return self[2]

    @property
    def P2(self) -> ByteString:
        return self[3]

    @property
    def Lc(self) -> ByteString:
        match self.__case:
            case CommandCase.Case1 | CommandCase.Case2S | CommandCase.Case2E:
                raise ValueError(
                    F'Command APDU has no Lc field ({self.case.value})')

            case CommandCase.Case3S | CommandCase.Case4S:
                return self[4]

            case CommandCase.Case3E | CommandCase.Case4E:
                return self[4:7]

    @property
    def data_field(self) -> ByteString:
        match self.case:
            case CommandCase.Case1 | CommandCase.Case2S | CommandCase.Case2E:
                raise ValueError(
                    F'Command APDU has no Data field ({self.case.value})')

            case CommandCase.Case3S:
                return self[5:]

            case CommandCase.Case4S:
                return self[5:-1]

            case CommandCase.Case3E:
                return self[7:]

            case CommandCase.Case4E:
                return self[7:-2]

    @property
    def Le(self) -> ByteString:
        match self.case:
            case CommandCase.Case1 | CommandCase.Case3S | CommandCase.Case3E:
                raise ValueError(
                    F'Command APDU has no Le field ({self.case.value})')

            case CommandCase.Case2S | CommandCase.Case4S:
                return self[-1]

            case CommandCase.Case2E | CommandCase.Case4E:
                return self[-2:]

    @property
    def Ne(self) -> int:
        match self.case:
            case CommandCase.Case1 | CommandCase.Case3S | CommandCase.Case3E:
                raise ValueError(
                    F'Command APDU has no Le field ({self.case.value})')

            case CommandCase.Case2S | CommandCase.Case4S:
                return 256 if self[-1] == '00' else int(self[-1])

            case CommandCase.Case2E | CommandCase.Case4E:
                return 65536 if self[-2:] == '0000' else int(self[-2:])

    def updated_Ne(self, Ne: int) -> CommandApdu:
        match self.case:
            case CommandCase.Case1 | CommandCase.Case3S | CommandCase.Case3E:
                raise ValueError(
                    F'Command APDU has no Le field ({self.case.value})')

            case CommandCase.Case2S:
                return CommandApdu(self.CLA, self.INS, self.P1, self.P2, data_field=None, Ne=Ne)

            case CommandCase.Case4S:
                return CommandApdu(self.CLA, self.INS, self.P1, self.P2, data_field=self.data_field, Ne=Ne)

            case CommandCase.Case2E | CommandCase.Case4E:
                raise ValueError(
                    F"Cannot update Le with APDU {self.case.value}")


def CAPDU(apdu: str | ByteString) -> CommandApdu:
    """CAPDU(): creates a CommandApdu object
    """
    match apdu:
        case str():
            _apdu = ByteString(apdu)
        case ByteString():
            _apdu = apdu
        case _:
            raise TypeError(
                F"CAPDU(): type {type(apdu)} not supported for argument apdu")

    header = _apdu[0:4].blocks(1)
    match len(_apdu):
        case l if l < 4:
            raise ValueError(
                F'CAPDU(): wrong Command APDU length, expected 4 or more bytes but received {_apdu}')

        case 4:
            # Case 1
            return CommandApdu(*header, data_field=None, Ne=None)

        case 5:
            # Case 2S
            Ne = 256 if _apdu[4] == '00' else int(_apdu[4])
            return CommandApdu(*header, data_field=None, Ne=Ne)

        case _:
            if _apdu[4] != '00':
                if len(_apdu) == 5 + int(_apdu[4]):
                    # Case 3S
                    return CommandApdu(*header, data_field=_apdu[5:], Ne=None)

                elif len(_apdu) == 5 + int(_apdu[4]) + 1:
                    # Case 4S
                    Ne = 256 if _apdu[4] == '00' else int(_apdu[4])
                    return CommandApdu(*header, data_field=_apdu[5:], Ne=Ne)

                else:
                    raise ValueError(
                        F'APDU(): wrong length, expected {5+int(_apdu[4])} bytes for Case 3s or {5+int(_apdu[4])+1} bytes for Case 4s but received {len(_apdu)} bytes instead')

            else:
                # Extended length cases
                if len(_apdu) == 7:
                    # Case 2E
                    Ne = 65536 if _apdu[4] == '00' else int(_apdu[4])
                    return CommandApdu(*header, data_field=None, Ne=Ne)

                elif len(_apdu) == 7 + int(_apdu[5:7]):
                    # Case 3E
                    return CommandApdu(*header, data_field=_apdu[7:], Ne=None)

                elif len(_apdu) == 7 + int(_apdu[5:7]) + 2:
                    # Case 4E
                    Ne = 65536 if _apdu[-2:] == '0000' else int(_apdu[-2:])
                    return CommandApdu(*header, data_field=_apdu[7:], Ne=None)

                else:
                    raise ValueError(
                        F'RAPDU(): wrong Command APDU length: expected {7 + int(_apdu[5:7])} bytes for Case 3e or {7 + int(_apdu[5:7]) + 2} bytes for Case 4e but received {len(_apdu)} bytes instead')


class StatusBytes(ByteString):
    def __init__(self, sw12: ByteString):
        if len(sw12) != 2:
            raise ValueError(F"Expected 2 bytes, received: {sw12}")

        if not (sw12.startswith('6') or sw12.startswith('9')):
            raise ValueError(F"Expected 6XXX or 9XXX value, received: {sw12}")

        if sw12.startswith('60'):
            raise ValueError(F"60XX in invalid, received: {sw12}")

        super().__init__(str(sw12))

    @property
    def state(self) -> ResponseProcessingState:
        match self:
            case '9000':
                return ResponseProcessingState.Normal
            case sw12 if sw12.startswith('61'):
                return ResponseProcessingState.Normal

            case sw12 if sw12.startswith('62') or sw12.startswith('63'):
                return ResponseProcessingState.Warning

            case sw12 if sw12.startswith('64') or sw12.startswith('65') or sw12.startswith('66'):
                return ResponseProcessingState.ExecutionError

            case sw12 if sw12.startswith('67') or sw12.startswith('68') or sw12.startswith('69') or sw12.startswith('6A') or sw12.startswith('6B') or sw12.startswith('6C') or sw12.startswith('6D') or sw12.startswith('6E') or sw12.startswith('6F'):
                return ResponseProcessingState.CheckingError

            case _:
                raise ValueError(F"Unknown processing state: {self}")

    @property
    def meaning(self) -> str:
        match self:
            case '9000':
                return 'No further qualification'

            case sw12 if sw12.startswith('61'):
                return 'SW2 encodes the number of data bytes still available'

            case sw12 if sw12.startswith('62'):
                match sw12[1]:
                    case '00':
                        return 'No information given'
                    case '81':
                        return 'Part of returned data may be corrupted'
                    case '82':
                        return 'End of file or record reached before reading Ne bytes'
                    case '83':
                        return 'Selected file deactivated'
                    case '84':
                        return 'File control information not formatted according to ISO7816-4 5.3.3'
                    case '85':
                        return 'Selected file in termination state'
                    case '86':
                        return 'No input data available from a sensor on the card'
                    case _:
                        return 'State of non-volatile memory is unchanged'

            case sw12 if sw12.startswith('63'):
                match sw12[1]:
                    case '00':
                        return 'No information given'
                    case '81':
                        return 'File filled up by the last write'
                    case sw2 if sw2.startswith('C'):
                        return F'Counter = {int(str(sw2), 16)-12}'
                    case _:
                        return 'State of non-volatile memory has changed(further qualification in SW2)'

            case sw12 if sw12.startswith('64'):
                match sw12[1]:
                    case '00':
                        return 'Execution error'
                    case '01':
                        return 'Immediate response required by the card'
                    case sw2 if int(str(sw2), 16) >= 0x02 and int(str(sw2), 16) <= 0x80:
                        return 'Triggering by the card'
                    case _:
                        return 'Unknown meaning'

            case sw12 if sw12.startswith('65'):
                match sw12[1]:
                    case '00':
                        return 'No information given'
                    case '81':
                        return 'Memory failure'
                    case _:
                        return 'Unknown meaning'

            case sw12 if sw12.startswith('66'):
                return 'Security-related issues'

            case '6700':
                return 'Wrong length; no further indication'

            case sw12 if sw12.startswith('68'):
                match sw12[1]:
                    case '00':
                        return 'No information given'
                    case '81':
                        return 'Logical channel not supported'
                    case '82':
                        return 'Secure messaging not supported'
                    case '83':
                        return 'Last command of the chain expected'
                    case '84':
                        return 'Command chaining not supported'
                    case _:
                        return 'Functions in CLA not supported (further qualification in SW2)'

            case sw12 if sw12.startswith('69'):
                match sw12[1]:
                    case '00':
                        return 'No information given'
                    case '81':
                        return 'Command incompatible with file structure'
                    case '82':
                        return 'Security status not satisfied'
                    case '83':
                        return 'Authentication method blocked'
                    case '84':
                        return 'Reference data not usable'
                    case '85':
                        return 'Conditions of use not satisfied'
                    case '86':
                        return 'Command not allowed (no current EF)'
                    case '87':
                        return 'Expected secure messaging data objects missing'
                    case '88':
                        return 'Incorrect secure messaging data objects'
                    case _:
                        return 'Command not allowed (further qualification in SW2)'

            case sw12 if sw12.startswith('6A'):
                match sw12[1]:
                    case '00':
                        return 'No information given'
                    case '80':
                        return 'Incorrect parameters in the command data field'
                    case '81':
                        return 'Function not supported'
                    case '82':
                        return 'File or application not found'
                    case '83':
                        return 'Record not found'
                    case '84':
                        return 'Not enough memory space in the file'
                    case '85':
                        return 'Nc inconsistent with TLV structure'
                    case '86':
                        return 'Incorrect parameters P1-P2'
                    case '87':
                        return 'Nc inconsistent with parameters P1-P2'
                    case '88':
                        return 'Referenced data or reference data not found (exact meaning depending on the command)'
                    case '89':
                        return 'File already exists'
                    case '8A':
                        return 'DF name already exists'
                    case _:
                        return 'Wrong parameters P1-P2 (further qualification in SW2)'

            case '6B00':
                return 'Wrong parameters P1-P2'

            case sw12 if sw12.startswith('6C'):
                return 'Wrong Le field; SW2 encodes the exact number of available data bytes'

            case '6D00':
                return 'Instruction code not supported or invalid'

            case '6E00':
                return 'Class not supported'

            case '6F00':
                return 'No precise diagnosis'

            case _:
                return 'Unkown meaning'


class ResponseApdu(ByteString):
    def __init__(self, response: ByteString):
        if len(response) < 2:
            raise ValueError(
                F"Expecting reponse of at least 2 bytes, received: {response}")
        super().__init__(str(response))

    @property
    def body(self) -> ByteString:
        if len(self) > 2:
            return self[0:-2]
        else:
            raise ValueError(F"No response body")

    @property
    def SW12(self) -> StatusBytes:
        return StatusBytes(self[-2:])

    @property
    def SW1(self) -> ByteString:
        return self.SW12[0]

    @property
    def SW2(self) -> ByteString:
        return self.SW12[1]

    @property
    def StatusBytes(self) -> StatusBytes:
        return self.SW12


def RAPDU(apdu: str | ByteString) -> ResponseApdu:
    """RAPDU(): creates a CommandApdu object
    """
    match apdu:
        case str():
            return ResponseApdu(ByteString(apdu))
        case ByteString():
            return ResponseApdu(apdu)
        case _:
            raise TypeError(
                F"RAPDU(): type {type(apdu)} not supported for argument apdu")
