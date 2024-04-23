"""emv_key_derivation.py
"""
# Standard library imports

# Third party imports
try:
    from icecream import ic
    ic.disable()
except ImportError:  # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


# Local application imports
from common.binary import ByteString
from emv.key_management import master_key_derivation_A


# Example script
if __name__ == '__main__':
    ic.enable()
    ic.includeContext = True

    ic('Mastercard key derivation:')
    MASTERCARD_PAN = '5413123456784808'
    MASTERCARD_PSN = '00'
    MDK = ByteString('01234567899876543210012345678998')
    ic(MDK, MASTERCARD_PAN, MASTERCARD_PSN)
    MASTERCARD_UDK = master_key_derivation_A(
        MDK, MASTERCARD_PAN, MASTERCARD_PSN)
    ic(MASTERCARD_UDK)

    ic('Visa key derivation:')
    VISA_PAN = '4761739001010010'
    VISA_PSN = '00'

    ic(MDK, VISA_PAN, VISA_PSN)

    VISA_UDK = master_key_derivation_A(MDK, VISA_PAN, VISA_PSN)

    ic(VISA_UDK)
