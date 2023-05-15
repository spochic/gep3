"""intlist.py
"""

# Standard library imports

# Third party imports

# Local application imports


# Definitions
def to_hstr(intlist_in, command_name='()', arg_name=''):
    """to_hstr()
    """
    hstr = ''
    for i in intlist_in:
        if not isinstance(i, int):
            raise TypeError(
                F"{command_name}: wrong element in {arg_name}: {i}")

        hstr += F"{i:02X}"

    return hstr


def is_int_list(intlist: list[int], command_name='()', arg_name='') -> bool:
    for i in intlist:
        if not isinstance(i, int):
            raise TypeError(
                F"{command_name}: wrong element in {arg_name}: expected int, received {type(i)} ({i})")
        elif i < 0 or i > 255:
            return False

    return True
