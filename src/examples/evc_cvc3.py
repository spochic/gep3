"""evc_cvc3.py
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
from emv.dsc import generate_ivcvc3, generate_cvc3


# Example script
if __name__ == '__main__':
    ic.enable()
    ic.includeContext = True

    ic('Mastercard card data:')
    PAN = '5413123456784808'
    PSN = '00'
    EXPY_DATE = '1220'
    ic(PAN, PSN, EXPY_DATE)

    ic('Mastercard key derivation:')
    MDK = ByteString('01234567899876543210012345678998')
    ic(MDK)
    UDK = master_key_derivation_A(MDK, PAN, PSN)
    ic(UDK)

    ic('Mastercard IVCVC3 computation:')
    TRACK2_EQUIVALENT = F'{PAN}D{EXPY_DATE}0000000000000000F'
    ic(TRACK2_EQUIVALENT)
    IC_CVC3 = generate_ivcvc3(UDK, TRACK2_EQUIVALENT)
    ic(IC_CVC3)

    ic('Mastercard CVC3 computation')
    UNPREDICTABLE_NUMBER = '00000000'
    ic(UNPREDICTABLE_NUMBER)
    for ATC in [F'{atc:04X}' for atc in range(1, 6)]:
        block = F'{IC_CVC3}{UNPREDICTABLE_NUMBER}{ATC}'
        ic(ATC, block)
        CVC3 = generate_cvc3(UDK, block)[-3:]
        ic(CVC3)
