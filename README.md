# SPJINCS-SM3
An attempt for ISC

## Experimental parameter set: sphincs-sm3-224f

This repository contains an experimental SM3 backend and a truncated-output
parameter set named `sphincs-sm3-224f`.

The experiment follows the waterline suggested by the SHA-256 category-five
analysis: if the practical concrete bottleneck is about 2^217.4 work, using
256-bit `n` everywhere gives signature bytes that do not buy meaningful
end-to-end security in that model.  The experimental set therefore truncates
SM3 to `n = 28` bytes, i.e. 224 bits, while keeping the `256f` tree/FORS shape:

```text
n = 28
h = 68
d = 17
a = 9
k = 35
w = 16
```

The SPHINCS+ signature length formula used by the reference code is:

```text
sig_bytes = n + (a + 1) * k * n + d * len * n + h * n
len       = len1 + len2
len1      = 8n / log2(w)
len2      = floor(log_w(len1 * (w - 1))) + 1
```

For `sphincs-sha2-256f`, this is:

```text
n=32, len=67, sig_bytes=49856
```

For `sphincs-sm3-224f`, this is:

```text
n=28, len=59, sig_bytes=39816
```

The reduction is 10040 bytes, or about 20.14%.

Build and test, on a machine with `make` and `gcc` available:

```sh
cd ref
make clean
make test/spx PARAMS=sphincs-sm3-224f THASH=robust
./test/spx
```

## Shorter experimental set: sphincs-sm3-224f-short

For a more aggressive size/speed tradeoff, `sphincs-sm3-224f-short` keeps
`n = 28` but changes:

```text
h = 64
d = 16
a = 8
k = 33
w = 256
```

This keeps height-4 subtrees and about `2^64` leaf capacity, uses the 192f FORS
shape, and reduces WOTS length from 59 to 30.  The signature length is:

```text
sig_bytes = 23576
```

This is 26280 bytes shorter than `sphincs-sha2-256f`, or about 52.71%.  The
tradeoff is speed: `w = 256` makes WOTS chains much longer than `w = 16`.

```sh
cd ref
make clean
make test/spx PARAMS=sphincs-sm3-224f-short THASH=robust
./test/spx
```
