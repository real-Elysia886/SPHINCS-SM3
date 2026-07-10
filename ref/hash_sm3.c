#include <stdint.h>
#include <string.h>

#include "address.h"
#include "utils.h"
#include "params.h"
#include "hash.h"
#include "sm3.h"

void initialize_hash_function(spx_ctx *ctx)
{
    seed_state(ctx);
}

void prf_addr(unsigned char *out, const spx_ctx *ctx,
              const uint32_t addr[8])
{
    uint8_t sm3_state[40];
    unsigned char buf[SPX_SM3_ADDR_BYTES + SPX_N];
    unsigned char outbuf[SPX_SM3_OUTPUT_BYTES];

    memcpy(sm3_state, ctx->state_seeded, 40 * sizeof(uint8_t));
    memcpy(buf, addr, SPX_SM3_ADDR_BYTES);
    memcpy(buf + SPX_SM3_ADDR_BYTES, ctx->sk_seed, SPX_N);

    sm3_inc_finalize(outbuf, sm3_state, buf, SPX_SM3_ADDR_BYTES + SPX_N);
    memcpy(out, outbuf, SPX_N);
}

void gen_message_random(unsigned char *R, const unsigned char *sk_prf,
                        const unsigned char *optrand,
                        const unsigned char *m, unsigned long long mlen,
                        const spx_ctx *ctx)
{
    (void)ctx;

    unsigned char buf[SPX_SM3_BLOCK_BYTES + SPX_SM3_OUTPUT_BYTES];
    uint8_t state[40];
    unsigned int i;

#if SPX_N > SPX_SM3_BLOCK_BYTES
    #error "Currently only supports SPX_N of at most SPX_SM3_BLOCK_BYTES"
#endif

    for (i = 0; i < SPX_N; i++) {
        buf[i] = 0x36 ^ sk_prf[i];
    }
    memset(buf + SPX_N, 0x36, SPX_SM3_BLOCK_BYTES - SPX_N);

    sm3_inc_init(state);
    sm3_inc_blocks(state, buf, 1);

    memcpy(buf, optrand, SPX_N);

    if (SPX_N + mlen < SPX_SM3_BLOCK_BYTES) {
        memcpy(buf + SPX_N, m, (size_t)mlen);
        sm3_inc_finalize(buf + SPX_SM3_BLOCK_BYTES, state, buf, (size_t)mlen + SPX_N);
    } else {
        memcpy(buf + SPX_N, m, SPX_SM3_BLOCK_BYTES - SPX_N);
        sm3_inc_blocks(state, buf, 1);

        m += SPX_SM3_BLOCK_BYTES - SPX_N;
        mlen -= SPX_SM3_BLOCK_BYTES - SPX_N;
        sm3_inc_finalize(buf + SPX_SM3_BLOCK_BYTES, state, m, (size_t)mlen);
    }

    for (i = 0; i < SPX_N; i++) {
        buf[i] = 0x5c ^ sk_prf[i];
    }
    memset(buf + SPX_N, 0x5c, SPX_SM3_BLOCK_BYTES - SPX_N);

    sm3(buf, buf, SPX_SM3_BLOCK_BYTES + SPX_SM3_OUTPUT_BYTES);
    memcpy(R, buf, SPX_N);
}

void hash_message(unsigned char *digest, spx_tree_index *tree,
                  uint32_t *leaf_idx,
                  const unsigned char *R, const unsigned char *pk,
                  const unsigned char *m, unsigned long long mlen,
                  const spx_ctx *ctx)
{
    (void)ctx;
#define SPX_TREE_BITS (SPX_TREE_HEIGHT * (SPX_D - 1))
#define SPX_TREE_BYTES ((SPX_TREE_BITS + 7) / 8)
#define SPX_LEAF_BITS SPX_TREE_HEIGHT
#define SPX_LEAF_BYTES ((SPX_LEAF_BITS + 7) / 8)
#define SPX_DGST_BYTES (SPX_FORS_MSG_BYTES + SPX_TREE_BYTES + SPX_LEAF_BYTES)

    unsigned char seed[2 * SPX_N + SPX_SM3_OUTPUT_BYTES];

#if (SPX_SM3_BLOCK_BYTES & (SPX_SM3_BLOCK_BYTES - 1)) != 0
    #error "Assumes that SPX_SM3_BLOCK_BYTES is a power of 2"
#endif
#define SPX_INBLOCKS (((SPX_N + SPX_PK_BYTES + SPX_SM3_BLOCK_BYTES - 1) & \
                        -SPX_SM3_BLOCK_BYTES) / SPX_SM3_BLOCK_BYTES)
    unsigned char inbuf[SPX_INBLOCKS * SPX_SM3_BLOCK_BYTES];

    unsigned char buf[SPX_DGST_BYTES];
    unsigned char *bufp = buf;
    uint8_t state[40];

    sm3_inc_init(state);

    memcpy(inbuf, R, SPX_N);
    memcpy(inbuf + SPX_N, pk, SPX_PK_BYTES);

    if (SPX_N + SPX_PK_BYTES + mlen < SPX_INBLOCKS * SPX_SM3_BLOCK_BYTES) {
        memcpy(inbuf + SPX_N + SPX_PK_BYTES, m, (size_t)mlen);
        sm3_inc_finalize(seed + 2 * SPX_N, state, inbuf,
                         (size_t)mlen + SPX_N + SPX_PK_BYTES);
    } else {
        memcpy(inbuf + SPX_N + SPX_PK_BYTES, m,
               SPX_INBLOCKS * SPX_SM3_BLOCK_BYTES - SPX_N - SPX_PK_BYTES);
        sm3_inc_blocks(state, inbuf, SPX_INBLOCKS);

        m += SPX_INBLOCKS * SPX_SM3_BLOCK_BYTES - SPX_N - SPX_PK_BYTES;
        mlen -= SPX_INBLOCKS * SPX_SM3_BLOCK_BYTES - SPX_N - SPX_PK_BYTES;
        sm3_inc_finalize(seed + 2 * SPX_N, state, m, (size_t)mlen);
    }

    memcpy(seed, R, SPX_N);
    memcpy(seed + SPX_N, pk, SPX_N);
    mgf1_sm3(bufp, SPX_DGST_BYTES, seed, 2 * SPX_N + SPX_SM3_OUTPUT_BYTES);

    memcpy(digest, bufp, SPX_FORS_MSG_BYTES);
    bufp += SPX_FORS_MSG_BYTES;

#if SPX_TREE_BITS > 128
    #error For given height and depth, 128 bits cannot represent all subtrees
#endif

    if (SPX_D == 1) {
        tree->high = 0;
        tree->low = 0;
    } else {
        tree_index_from_bytes(tree, bufp, SPX_TREE_BYTES, SPX_TREE_BITS);
    }
    bufp += SPX_TREE_BYTES;

    *leaf_idx = (uint32_t)bytes_to_ull(bufp, SPX_LEAF_BYTES);
    *leaf_idx &= (~(uint32_t)0) >> (32 - SPX_LEAF_BITS);
}
