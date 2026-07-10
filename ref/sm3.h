#ifndef SPX_SM3_H
#define SPX_SM3_H

#include "params.h"
#include "context.h"

#include <stddef.h>
#include <stdint.h>

#define SPX_SM3_BLOCK_BYTES 64
#define SPX_SM3_OUTPUT_BYTES 32
#ifndef SPX_SM3_ADDR_BYTES
#define SPX_SM3_ADDR_BYTES 22
#endif

#if SPX_SM3_OUTPUT_BYTES < SPX_N
    #error Linking against SM3 with N larger than 32 bytes is not supported
#endif

void sm3_inc_init(uint8_t *state);
void sm3_inc_blocks(uint8_t *state, const uint8_t *in, size_t inblocks);
void sm3_inc_finalize(uint8_t *out, uint8_t *state, const uint8_t *in, size_t inlen);
void sm3(uint8_t *out, const uint8_t *in, size_t inlen);

#define mgf1_sm3 SPX_NAMESPACE(mgf1_sm3)
void mgf1_sm3(unsigned char *out, unsigned long outlen,
              const unsigned char *in, unsigned long inlen);

#define seed_state SPX_NAMESPACE(seed_state)
void seed_state(spx_ctx *ctx);

#endif
