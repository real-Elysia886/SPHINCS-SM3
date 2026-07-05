#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "sm3.h"

static uint32_t load_be32(const uint8_t *x)
{
    return ((uint32_t)x[0] << 24) | ((uint32_t)x[1] << 16) |
           ((uint32_t)x[2] << 8) | (uint32_t)x[3];
}

static uint64_t load_be64(const uint8_t *x)
{
    uint64_t r = 0;
    size_t i;

    for (i = 0; i < 8; i++) {
        r = (r << 8) | x[i];
    }
    return r;
}

static void store_be32(uint8_t *x, uint32_t u)
{
    x[0] = (uint8_t)(u >> 24);
    x[1] = (uint8_t)(u >> 16);
    x[2] = (uint8_t)(u >> 8);
    x[3] = (uint8_t)u;
}

static void store_counter32(uint8_t *x, uint32_t u)
{
    store_be32(x, u);
}

static void store_be64(uint8_t *x, uint64_t u)
{
    int i;

    for (i = 7; i >= 0; i--) {
        x[i] = (uint8_t)u;
        u >>= 8;
    }
}

static uint32_t rotl32(uint32_t x, unsigned int n)
{
    n &= 31;
    return n == 0 ? x : ((x << n) | (x >> (32 - n)));
}

#define ROTL32(x, n) rotl32((x), (n))
#define FF0(x, y, z) ((x) ^ (y) ^ (z))
#define FF1(x, y, z) (((x) & (y)) | ((x) & (z)) | ((y) & (z)))
#define GG0(x, y, z) ((x) ^ (y) ^ (z))
#define GG1(x, y, z) (((x) & (y)) | ((~(x)) & (z)))
#define P0(x) ((x) ^ ROTL32((x), 9) ^ ROTL32((x), 17))
#define P1(x) ((x) ^ ROTL32((x), 15) ^ ROTL32((x), 23))

static size_t sm3_compress_blocks(uint8_t *statebytes, const uint8_t *in, size_t inlen)
{
    uint32_t state[8];
    size_t i;

    for (i = 0; i < 8; i++) {
        state[i] = load_be32(statebytes + 4 * i);
    }

    while (inlen >= SPX_SM3_BLOCK_BYTES) {
        uint32_t w[68];
        uint32_t wp[64];
        uint32_t a, b, c, d, e, f, g, h;
        uint32_t ss1, ss2, tt1, tt2;
        uint32_t t;
        size_t j;

        for (j = 0; j < 16; j++) {
            w[j] = load_be32(in + 4 * j);
        }
        for (j = 16; j < 68; j++) {
            w[j] = P1(w[j - 16] ^ w[j - 9] ^ ROTL32(w[j - 3], 15)) ^
                   ROTL32(w[j - 13], 7) ^ w[j - 6];
        }
        for (j = 0; j < 64; j++) {
            wp[j] = w[j] ^ w[j + 4];
        }

        a = state[0];
        b = state[1];
        c = state[2];
        d = state[3];
        e = state[4];
        f = state[5];
        g = state[6];
        h = state[7];

        for (j = 0; j < 64; j++) {
            t = j < 16 ? 0x79cc4519U : 0x7a879d8aU;
            ss1 = ROTL32((ROTL32(a, 12) + e + ROTL32(t, (unsigned int)(j & 31))) & 0xffffffffU, 7);
            ss2 = ss1 ^ ROTL32(a, 12);
            if (j < 16) {
                tt1 = (FF0(a, b, c) + d + ss2 + wp[j]) & 0xffffffffU;
                tt2 = (GG0(e, f, g) + h + ss1 + w[j]) & 0xffffffffU;
            } else {
                tt1 = (FF1(a, b, c) + d + ss2 + wp[j]) & 0xffffffffU;
                tt2 = (GG1(e, f, g) + h + ss1 + w[j]) & 0xffffffffU;
            }
            d = c;
            c = ROTL32(b, 9);
            b = a;
            a = tt1;
            h = g;
            g = ROTL32(f, 19);
            f = e;
            e = P0(tt2);
        }

        state[0] ^= a;
        state[1] ^= b;
        state[2] ^= c;
        state[3] ^= d;
        state[4] ^= e;
        state[5] ^= f;
        state[6] ^= g;
        state[7] ^= h;

        in += SPX_SM3_BLOCK_BYTES;
        inlen -= SPX_SM3_BLOCK_BYTES;
    }

    for (i = 0; i < 8; i++) {
        store_be32(statebytes + 4 * i, state[i]);
    }

    return inlen;
}

static const uint8_t sm3_iv[32] = {
    0x73, 0x80, 0x16, 0x6f, 0x49, 0x14, 0xb2, 0xb9,
    0x17, 0x24, 0x42, 0xd7, 0xda, 0x8a, 0x06, 0x00,
    0xa9, 0x6f, 0x30, 0xbc, 0x16, 0x31, 0x38, 0xaa,
    0xe3, 0x8d, 0xee, 0x4d, 0xb0, 0xfb, 0x0e, 0x4e
};

void sm3_inc_init(uint8_t *state)
{
    size_t i;

    for (i = 0; i < 32; i++) {
        state[i] = sm3_iv[i];
    }
    for (i = 32; i < 40; i++) {
        state[i] = 0;
    }
}

void sm3_inc_blocks(uint8_t *state, const uint8_t *in, size_t inblocks)
{
    uint64_t bytes = load_be64(state + 32);

    sm3_compress_blocks(state, in, SPX_SM3_BLOCK_BYTES * inblocks);
    bytes += SPX_SM3_BLOCK_BYTES * inblocks;
    store_be64(state + 32, bytes);
}

void sm3_inc_finalize(uint8_t *out, uint8_t *state, const uint8_t *in, size_t inlen)
{
    uint8_t padded[128];
    uint64_t bytes = load_be64(state + 32) + inlen;
    size_t i;

    sm3_compress_blocks(state, in, inlen);
    in += inlen;
    inlen &= 63;
    in -= inlen;

    for (i = 0; i < inlen; i++) {
        padded[i] = in[i];
    }
    padded[inlen] = 0x80;

    if (inlen < 56) {
        memset(padded + inlen + 1, 0, 56 - inlen - 1);
        store_be64(padded + 56, bytes << 3);
        sm3_compress_blocks(state, padded, 64);
    } else {
        memset(padded + inlen + 1, 0, 120 - inlen - 1);
        store_be64(padded + 120, bytes << 3);
        sm3_compress_blocks(state, padded, 128);
    }

    memcpy(out, state, SPX_SM3_OUTPUT_BYTES);
}

void sm3(uint8_t *out, const uint8_t *in, size_t inlen)
{
    uint8_t state[40];

    sm3_inc_init(state);
    sm3_inc_finalize(out, state, in, inlen);
}

void mgf1_sm3(unsigned char *out, unsigned long outlen,
              const unsigned char *in, unsigned long inlen)
{
    uint8_t inbuf[inlen + 4];
    unsigned char outbuf[SPX_SM3_OUTPUT_BYTES];
    unsigned long i;

    memcpy(inbuf, in, inlen);

    for (i = 0; (i + 1) * SPX_SM3_OUTPUT_BYTES <= outlen; i++) {
        store_counter32(inbuf + inlen, (uint32_t)i);
        sm3(out, inbuf, inlen + 4);
        out += SPX_SM3_OUTPUT_BYTES;
    }

    if (outlen > i * SPX_SM3_OUTPUT_BYTES) {
        store_counter32(inbuf + inlen, (uint32_t)i);
        sm3(outbuf, inbuf, inlen + 4);
        memcpy(out, outbuf, outlen - i * SPX_SM3_OUTPUT_BYTES);
    }
}

void seed_state(spx_ctx *ctx)
{
    uint8_t block[SPX_SM3_BLOCK_BYTES];
    size_t i;

    for (i = 0; i < SPX_N; i++) {
        block[i] = ctx->pub_seed[i];
    }
    for (i = SPX_N; i < SPX_SM3_BLOCK_BYTES; i++) {
        block[i] = 0;
    }

    sm3_inc_init(ctx->state_seeded);
    sm3_inc_blocks(ctx->state_seeded, block, 1);
}
