# Explanation

*This assumes you have a decent understanding of modular arithmetic*

## Elliptic Curve Math (`primitives.py`)

### Basics

I implement the `secp256k1` curve here, which is defined by the equation $y^2 = x^3 + 7$.
Importantly, $x$ and $y$ are both over the finite field $p = 2^{256} - 2^{32} - 977$.
This means all numbers are integers and all operations are done modulo $p$.

> Simplified example: consider the same curve $y^2 = x^3 + 7$ but modulo $p = 17$.
> Then the point $(x=1, y=12)$ is on the curve: $y^2 = 144 \equiv 8 \pmod{17}$, $x^3 + 7 = 8$.

### Point Addition

Point addition is the main operation on elliptic curves.

Over the real numbers, in order to add $P$ and $Q$, you draw a line through them, find the third intersection point $R'$ (there always is one), and then reflect it across the x-axis (negate the y-coordinate) to get $R$.

> [You may find a better visualization online here.](https://certicom.com/content/certicom/en/21-elliptic-curve-addition-a-geometric-approach.html)

Over finite fields, we have the same idea, but it's modular arithmetic, and there are some ugly algebraic formulas.

### Point Addition Formulas

Given $(x_1, y_1)$ and $(x_2, y_2)$:

- Their slope is $m = \frac{y_2 - y_1}{x_2 - x_1}$ (division is multiplying by the modular inverse)
- The resulting point $(x_3, y_3)$ is given by:
  - $x_3 = m^2 - x_1 - x_2 \pmod{p}$
  - $y_3 = m(x_1 - x_3) - y_1 \pmod{p}$

If you are trying to add a point to itself (point doubling), the slope is $m = y' = \frac{3x^2}{2y}$. (You can derive this by implicitly differentiating the curve equation.)

### Extra Properties

- There is a point at infinity, which is like an identity element, but it's not super important here.
- The curve has an order $n \approx 2^{256} - 2^{128}$. Importantly, multiplying a point by `n+3` is the same as multiplying it by `3`, so we can reduce all scalar multiples modulo `n`.


## Signature Math

### Keys

You generate a random private key $d$ between $1$ and $n-1$.

Your public key is the point $Q = dG$.
($G$ is the generator point - basically a constant starter point set by the standard.)
It is hard to extract $d$ from $Q$ (the discrete logarithm problem).

### Signature Generation

Pick a random and secret integer $k$ between $1$ and $n-1$.
It's very important that $k$ is random, secret, and never reused!

Compute the point $R = kG$, and let $r$ be the x-coordinate of $R$, reduced modulo $n$.
(Reducing modulo $n$ is technically not super necessary and does not add any extra security, but it's what everyone does.)

Compute $s = k^{-1}(M + rd) \pmod{n}$, where $M$ is the (hash of the) message.

The signature is $r, s$ with public key $Q$.

### Signature Verification

Compute $u_1 = Ms^{-1} \pmod{n}$ and $u_2 = rs^{-1} \pmod{n}$.

Compute the point $R = u_1G + u_2Q$.

If the x-coordinate of $R$, reduced modulo $n$, equals $r$, the signature is valid.

### Signature Verification Correctness

Why does the verification work?

We have $s = k^{-1}(M + rd)$, so $s^{-1} = k(M+rd)^{-1}$. (Here all operations are modulo $n$.)

Then $u_1 = Mk(M+rd)^{-1}$ and $u_2 = rk(M+rd)^{-1}$.

Then:

$R = u_1G + u_2Q = u_1G + u_2dG = (u_1 + u_2d)G$

$= (Mk + rdk)(M+rd)^{-1} G$

$= k(M + rd)(M + rd)^{-1} G = kG$.

### Security

**If $k$ is known, the algorithm breaks.**

Because $s = k^{-1}(M + rd)$, if we know $s, k, M, r$, we can solve for $d$ (one equation, one unknown).

**But if $k$ is secret, forgery is difficult.**

Suppose I want to forge a signature for the message $M' = M + x$ for some $x$. Then $s' = k^{-1}(M + x + rd) = k^{-1}[(M + rd) + x] = s + k^{-1}x$.
I can't compute the new signature without knowing $k$.

If we keep $k$ secret and never reuse it, an attacker only knows $kG$ (they can calculate it from verifying the signature or by using $r$, the x-coordinate).
However, since it's difficult (in the "we believe that calculating it will take forever" sense) to get $k$ from $kG$, this is safe.

**Verification proves knowledge of $d$.**

Suppose we're trying to verify the authenticity of a signature $s$.
Our math tells us that $R = kG$ only if $s = k^{-1}(M + rd)$.

So if we have a verified signature, we know that the signer must have computed $s$ correctly, which requires knowledge of $d$.

The genius part is, $s$ is calculated in a way that it can be verified on the curve with $dG$ and $kG$, keeping $d$ and $k$ secret the whole time.
