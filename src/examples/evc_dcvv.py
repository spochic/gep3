"""evc_dcvv.py
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
from emv.dsc import generate_dcvv


# Example script
if __name__ == '__main__':
    ic.enable()
    ic.includeContext = True

    ic('Visa card data:')
    PAN = '4761739001010010'
    PSN = '00'
    EXPY_DATE = '1220'
    ic(PAN, PSN, EXPY_DATE)

    ic('Visa key derivation:')
    MDK = ByteString('2315208C9110AD402315208C9110AD40')
    ic(MDK)
    UDK = master_key_derivation_A(MDK, PAN, PSN)
    ic(UDK)

    ic('Visa dCVV computation:')
    for ATC in [F'{atc:04X}' for atc in range(1, 6)]:
        DCVV = generate_dcvv(UDK, PAN, ATC, EXPY_DATE)
        ic(ATC, DCVV)
