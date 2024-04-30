"""commands.py
"""

# Standard library imports
from typing import Optional


# Third party imports

# Local application imports
from common.binary import ByteString
from iso7816.apdu import CommandApdu
from iso7816.encodings import ClassByte as ISO_ClassByte
from .encodings import ClassByte, GetDataObject, FileOccurrence, ApplicationIdentifier


# Command APDUs defined by GP
class GetData(CommandApdu):
    def __init__(self, CLA: ClassByte, tag: ByteString, data: Optional[ByteString]):
        header = (CLA + ByteString('CA') + tag).blocks(1)
        if data is None:
            super().__init__(*header, data_field=None, Ne=256)
        else:
            super().__init__(*header, data_field=data, Ne=256)


def GET_DATA(CLA: ClassByte, tag: ByteString | GetDataObject, data: Optional[ByteString]) -> GetData:
    """GET_DATA: generate APDU for GET DATA command
    """
    if isinstance(tag, GetDataObject):
        if len(tag.value) == 2:
            P1 = ByteString('00')
            P2 = ByteString(tag.value)
        else:
            P1 = ByteString(tag.value[0:2])
            P2 = ByteString(tag.value[2:4])

    elif isinstance(tag, ByteString):
        P1 = tag[0:2]
        P2 = tag[2:4]

    else:
        raise TypeError(
            F"globalplatform.GET_DATA(): tag should be of type ByteString or GetDataObject, received: {type(tag)}")

    return GetData(CLA, P1+P2, data)


class Select(CommandApdu):
    def __init__(self, CLA: ISO_ClassByte, file_occurrence: FileOccurrence, aid: ByteString | ApplicationIdentifier):
        header = (
            CLA + ByteString(F'A404{file_occurrence:02X}')).blocks(1)

        match aid:
            case ApplicationIdentifier():
                if aid == ApplicationIdentifier.Default:
                    super().__init__(*header, data_field=None, Ne=256)
                else:
                    super().__init__(*header, data_field=ByteString(aid.value), Ne=256)
            case ByteString():
                super().__init__(*header, data_field=aid, Ne=256)
            case _:
                raise TypeError(
                    F"Select(): aid should be of type ByteString or ApplicationIdentifier, received: {type(aid)}")


def SELECT(CLA: ISO_ClassByte, file_occurrence: FileOccurrence, aid: ByteString | ApplicationIdentifier) -> Select:
    """SELECT(): generate CommandApdu for SELECT command (GlobalPlatform)
    """

    return Select(CLA, file_occurrence, aid)
