"""secp256k1 primitives"""


PRIME = 2**256 - 2**32 - 977
ORDER = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
G_X = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
G_Y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8


def verify_point(x: int, y: int) -> bool:
    """Verify that the point (x, y) is on the curve."""
    lhs = pow(y, 2, PRIME)
    rhs = (pow(x, 3, PRIME) + 7) % PRIME
    return lhs == rhs


def modular_divide(a: int, b: int) -> int:
    """Return a / b (mod PRIME)."""
    b_inv = pow(b, -1, PRIME)
    return (a * b_inv) % PRIME


def double_point(x: int, y: int) -> tuple[int, int]:
    """Double the point P = (x, y) and return Q = 2P = (x_2, y_2)."""
    # Differentiate:   y^2 = x^3 + 7
    #                y' 2y = 3x^2
    slope = modular_divide(3*x*x, 2*y)
    # Same formula as adding points
    x_new = (slope*slope - 2*x) % PRIME
    y_new = (slope*(x-x_new) - y) % PRIME
    return x_new, y_new


def add_points(x1: int, y1: int, x2: int, y2: int) -> tuple[int, int]:
    """Adds two points P = (x1, y1) and Q = (x2, y2) and returns R = P + Q = (x_new, y_new)."""
    assert (x1, y1) != (x2, y2)
    slope = modular_divide(y2 - y1, x2 - x1)
    # Derivations of these formulas are messy
    # I'm not going to investigate them too deeply right now
    x_new = (slope*slope - x1 - x2) % PRIME
    y_new = (slope*(x1-x_new) - y1) % PRIME
    return x_new, y_new


def scalar_multiply(x: int, y: int, k: int) -> tuple[int, int]:
    """Multiply point P = (x, y) by scalar k and return Q = kP = (x_new, y_new)."""
    assert k > 0
    assert k != ORDER, 'Multiplying by order results in infinity point'
    # Simple recursive doubling/halving implementation
    if k % 2 == 0:
        # (k/2)P + (k/2)P
        return double_point(*scalar_multiply(x, y, k // 2))
    elif k == 1:
        return x, y
    else:
        # P + ((k-1)/2)P + ((k-1)/2)P
        return add_points(x, y, *double_point(*scalar_multiply(x, y, k // 2)))


if __name__ == '__main__':
    assert verify_point(G_X, G_Y)
    assert verify_point(*double_point(G_X, G_Y))
    assert double_point(G_X, G_Y) == (89565891926547004231252920425935692360644145829622209833684329913297188986597,
                                      12158399299693830322967808612713398636155367887041628176798871954788371653930)
    assert scalar_multiply(G_X, G_Y, 2) == double_point(G_X, G_Y)
    assert verify_point(*scalar_multiply(G_X, G_Y, 123456789111222333444555))
    assert scalar_multiply(G_X, G_Y, 100) == (107303582290733097924842193972465022053148211775194373671539518313500194639752,
                                                 103795966108782717446806684023742168462365449272639790795591544606836007446638)
    assert scalar_multiply(G_X, G_Y, 2147483647) == (18845197221170589343906318257608747345355704040405879359276255241170402932467,
                                                        35869855410725365793927656664169024200680894402224297472548781181062428830648)
    print('All tests passed.')
