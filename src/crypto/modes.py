"""modes.py: Block cipher modes of operation
"""

# Standard library imports
from typing import Callable, Iterable

# Third party imports

# Local application imports
from common.binary import HexString


def ecb_encryption(enc: Callable, key: HexString, blocks: Iterable[HexString]) -> HexString:
    """ecb_encryption()
    """
    ciphertext_blocks = [enc(key, plaintext_block)
                         for plaintext_block in blocks]
    ciphertext = HexString('').join(ciphertext_blocks)

    return ciphertext


def ecb_decryption(dec: Callable[[HexString, HexString], HexString], key: HexString, blocks: Iterable[HexString]) -> HexString:
    """ecb_decryption()
    """
    plaintext_blocks = [dec(key, ciphertext_block)
                        for ciphertext_block in blocks]
    plaintext = HexString('').join(plaintext_blocks)

    return plaintext


def cbc_encryption(enc: Callable, key: HexString, blocks: Iterable[HexString], iv: HexString) -> HexString:
    """cbc_encryption()
    """
    tmp = iv
    ciphertext = HexString('')
    for plaintext_block in blocks:
        tmp = enc(key, tmp ^ plaintext_block)
        ciphertext += tmp

    return ciphertext


def cbc_decryption(dec: Callable, key: HexString, blocks: Iterable[HexString], iv: HexString) -> HexString:
    """cbc_decryption()
    """
    tmp = iv
    plaintext = HexString('')
    for ciphertext_block in blocks:
        plaintext += tmp ^ dec(key, ciphertext_block)
        tmp = ciphertext_block

    return plaintext
