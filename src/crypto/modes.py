"""modes.py: Block cipher modes of operation
"""

# Standard library imports
from typing import Callable, Iterable
from functools import reduce
from operator import __add__

# Third party imports

# Local application imports
from common.binary import ByteString


SymmetricCipher = Callable[[ByteString, ByteString], ByteString]


def ecb_encryption(enc: SymmetricCipher, key: ByteString, blocks: Iterable[ByteString]) -> ByteString:
    """ecb_encryption()
    """
    ciphertext_blocks = [enc(key, plaintext_block)
                         for plaintext_block in blocks]

    return reduce(__add__, ciphertext_blocks)


def ecb_decryption(dec: SymmetricCipher, key: ByteString, blocks: Iterable[ByteString]) -> ByteString:
    """ecb_decryption()
    """
    plaintext_blocks = [dec(key, ciphertext_block)
                        for ciphertext_block in blocks]

    return reduce(__add__, plaintext_blocks)


def cbc_encryption(enc: SymmetricCipher, key: ByteString, blocks: Iterable[ByteString], iv: ByteString) -> ByteString:
    """cbc_encryption()
    """
    tmp = iv
    ciphertext_blocks: list[ByteString] = []
    for plaintext_block in blocks:
        tmp = enc(key, tmp ^ plaintext_block)
        ciphertext_blocks.append(tmp)

    return reduce(__add__, ciphertext_blocks)


def cbc_decryption(dec: SymmetricCipher, key: ByteString, blocks: Iterable[ByteString], iv: ByteString) -> ByteString:
    """cbc_decryption()
    """
    tmp = iv
    plaintext_blocks: list[ByteString] = []
    for ciphertext_block in blocks:
        plaintext_blocks.append(tmp ^ dec(key, ciphertext_block))
        tmp = ciphertext_block

    return reduce(__add__, plaintext_blocks)
