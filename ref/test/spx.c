#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "../api.h"
#include "../address.h"
#include "../params.h"
#include "../randombytes.h"
#include "../utils.h"

#ifndef SPX_MLEN
#define SPX_MLEN 32
#endif

#ifndef SPX_SIGNATURES
#define SPX_SIGNATURES 1
#endif

static int test_wide_tree_index(void)
{
    static const unsigned char input[10] = {
        0x0a, 0xbc, 0xde, 0xf0, 0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc
    };
    static const unsigned char shifted[12] = {
        0x00, 0x00, 0x00, 0xab, 0xcd, 0xef,
        0x01, 0x23, 0x45, 0x67, 0x89, 0xab
    };
    static const unsigned char wide_address[12] = {
        0x00, 0x00, 0x0a, 0xbc, 0xde, 0xf0,
        0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc
    };
    unsigned char encoded[12];
    uint32_t address[8] = {0};
    spx_tree_index tree;

    tree_index_from_bytes(&tree, input, sizeof(input), 76);
    if (tree.high != 0xabc || tree.low != UINT64_C(0xdef0123456789abc)) {
        return -1;
    }
    if (tree_index_low_bits(&tree, 4) != 0x0c) {
        return -1;
    }
    set_tree_addr(address, &tree);
    if (SPX_TREE_ADDR_BYTES == 12
            && memcmp((unsigned char *)address + SPX_OFFSET_TREE,
                      wide_address, sizeof(wide_address)) != 0) {
        return -1;
    }
    tree_index_shift_right(&tree, 4);
    tree_index_to_bytes(encoded, sizeof(encoded), &tree);
    return memcmp(encoded, shifted, sizeof(encoded)) == 0 ? 0 : -1;
}

int main(void)
{
    int ret = 0;
    int i;

    /* Make stdout buffer more responsive. */
    setvbuf(stdout, NULL, _IONBF, 0);

    if (test_wide_tree_index() != 0) {
        printf("Wide tree-index helper test failed!\n");
        return -1;
    }
    printf("Wide tree-index helper test passed.\n");

    unsigned char pk[SPX_PK_BYTES];
    unsigned char sk[SPX_SK_BYTES];
    unsigned char *m = malloc(SPX_MLEN);
    unsigned char *sm = malloc(SPX_BYTES + SPX_MLEN);
    unsigned char *mout = malloc(SPX_BYTES + SPX_MLEN);
    unsigned long long smlen;
    unsigned long long mlen;

    if (m == NULL || sm == NULL || mout == NULL) {
        printf("allocation failed!\n");
        free(m);
        free(sm);
        free(mout);
        return -1;
    }

    randombytes(m, SPX_MLEN);

    printf("Generating keypair.. ");

    if (crypto_sign_keypair(pk, sk)) {
        printf("failed!\n");
        free(m);
        free(sm);
        free(mout);
        return -1;
    }
    printf("successful.\n");

    printf("Testing %d signatures.. \n", SPX_SIGNATURES);

    for (i = 0; i < SPX_SIGNATURES; i++) {
        printf("  - iteration #%d:\n", i);

        crypto_sign(sm, &smlen, m, SPX_MLEN, sk);

        if (smlen != SPX_BYTES + SPX_MLEN) {
            printf("  X smlen incorrect [%llu != %u]!\n",
                   smlen, SPX_BYTES + SPX_MLEN);
            ret = -1;
        }
        else {
            printf("    smlen as expected [%llu].\n", smlen);
        }

        /* Test if signature is valid. */
        if (crypto_sign_open(mout, &mlen, sm, smlen, pk)) {
            printf("  X verification failed!\n");
            ret = -1;
        }
        else {
            printf("    verification succeeded.\n");
        }

        /* Test if the correct message was recovered. */
        if (mlen != SPX_MLEN) {
            printf("  X mlen incorrect [%llu != %u]!\n", mlen, SPX_MLEN);
            ret = -1;
        }
        else {
            printf("    mlen as expected [%llu].\n", mlen);
        }
        if (memcmp(m, mout, SPX_MLEN)) {
            printf("  X output message incorrect!\n");
            ret = -1;
        }
        else {
            printf("    output message as expected.\n");
        }

        /* Test if flipping bits invalidates the signature (it should). */

        /* Flip one bit in the final message byte. Should invalidate. */
        sm[smlen - 1] ^= 1;
        if (!crypto_sign_open(mout, &mlen, sm, smlen, pk)) {
            printf("  X flipping a bit of m DID NOT invalidate signature!\n");
            ret = -1;
        }
        else {
            printf("    flipping a bit of m invalidates signature.\n");
        }
        sm[smlen - 1] ^= 1;

#ifdef SPX_TEST_INVALIDSIG
        int j;
        /* Flip one representative bit in every N-byte signature block. */
        for (j = 0; j < (int)(smlen - SPX_MLEN); j += SPX_N) {
            sm[j] ^= 1;
            if (!crypto_sign_open(mout, &mlen, sm, smlen, pk)) {
                printf("  X flipping bit %d DID NOT invalidate sig + m!\n", j);
                sm[j] ^= 1;
                ret = -1;
                break;
            }
            sm[j] ^= 1;
        }
        if (j >= (int)(smlen - SPX_MLEN)) {
            printf("    changing every sampled signature block invalidates signature.\n");
        }
#endif

        /* Run this last because successful in-place opening overwrites sm. */
        if (crypto_sign_open(sm, &mlen, sm, smlen, pk)) {
            printf("  X in-place verification failed!\n");
            ret = -1;
        }
        else {
            printf("    in-place verification succeeded.\n");
        }
    }

    free(m);
    free(sm);
    free(mout);

    return ret;
}
