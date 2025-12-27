"""Implements ECDSA signature and verification"""


import random

from primitives import *


def sign(message: int, private_key: int, nonce: int) -> tuple[int, int]:
    """Sign the message with the provided parameters and return (r, s)."""
    x1, y1 = scalar_multiply(G_X, G_Y, nonce)
    r = x1 % ORDER
    if r == 0:
        raise ValueError('Invalid nonce: r == 0')
    k_inv = pow(nonce, -1, ORDER)
    s = (k_inv * (message + r * private_key)) % ORDER
    return r, s


def verify(message: int, signature: tuple[int, int], public_key_point: tuple[int, int]) -> bool:
    """
    Verify the signature (r, s) for the message and public key point.
    Return True if valid, False otherwise.
    """
    r, s = signature
    assert 1 <= r < ORDER and 1 <= s < ORDER
    assert verify_point(*public_key_point)  # All valid points are part of the subgroup, so no need to check beyond this
    s_inv = pow(s, -1, ORDER)
    u1 = (message * s_inv) % ORDER
    u2 = (r * s_inv) % ORDER
    x1, y1 = add_points(*scalar_multiply(G_X, G_Y, u1),
                        *scalar_multiply(*public_key_point, u2))
    return r % ORDER == x1 % ORDER


if __name__ == '__main__':
    # Simple test case
    priv_key = 0x123456789abcdefcccccccccccccccc
    pub_key = scalar_multiply(G_X, G_Y, priv_key)
    msg = 0xdeadbeef
    nonce = random.randint(1, ORDER - 1)
    signature = sign(msg, priv_key, nonce)
    print(f'Signature: r={hex(signature[0])}, s={hex(signature[1])}')
    assert verify(msg, signature, pub_key)
    assert not verify(msg+1, signature, pub_key)
    print('Test passed!')