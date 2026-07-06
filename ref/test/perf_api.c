#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "../api.h"
#include "../randombytes.h"

#ifndef SPX_BENCH_ITERS
#define SPX_BENCH_ITERS 3
#endif

#ifndef SPX_MLEN
#define SPX_MLEN 64
#endif

static double elapsed_ms(clock_t start, clock_t stop)
{
    return 1000.0 * (double)(stop - start) / (double)CLOCKS_PER_SEC;
}

int main(void)
{
    unsigned char pk[SPX_PK_BYTES];
    unsigned char sk[SPX_SK_BYTES];
    unsigned char *m = malloc(SPX_MLEN);
    unsigned char *sm = malloc(SPX_BYTES + SPX_MLEN);
    unsigned char *mout = malloc(SPX_BYTES + SPX_MLEN);
    unsigned long long smlen = 0;
    unsigned long long mlen = 0;
    double keygen_ms = 0.0;
    double sign_ms = 0.0;
    double verify_ms = 0.0;
    clock_t start;
    clock_t stop;
    int i;

    setvbuf(stdout, NULL, _IONBF, 0);

    if (m == NULL || sm == NULL || mout == NULL) {
        fprintf(stderr, "allocation failed\n");
        free(m);
        free(sm);
        free(mout);
        return 1;
    }

    randombytes(m, SPX_MLEN);

    for (i = 0; i < SPX_BENCH_ITERS; i++) {
        start = clock();
        if (crypto_sign_keypair(pk, sk) != 0) {
            fprintf(stderr, "keygen failed\n");
            return 1;
        }
        stop = clock();
        keygen_ms += elapsed_ms(start, stop);
    }

    if (crypto_sign_keypair(pk, sk) != 0) {
        fprintf(stderr, "setup keygen failed\n");
        return 1;
    }

    for (i = 0; i < SPX_BENCH_ITERS; i++) {
        m[0] ^= (unsigned char)i;
        start = clock();
        if (crypto_sign(sm, &smlen, m, SPX_MLEN, sk) != 0) {
            fprintf(stderr, "sign failed\n");
            return 1;
        }
        stop = clock();
        sign_ms += elapsed_ms(start, stop);

        if (smlen != SPX_BYTES + SPX_MLEN) {
            fprintf(stderr, "unexpected signed-message length\n");
            return 1;
        }
    }

    if (crypto_sign(sm, &smlen, m, SPX_MLEN, sk) != 0) {
        fprintf(stderr, "setup sign failed\n");
        return 1;
    }

    for (i = 0; i < SPX_BENCH_ITERS; i++) {
        start = clock();
        if (crypto_sign_open(mout, &mlen, sm, smlen, pk) != 0) {
            fprintf(stderr, "verify failed\n");
            return 1;
        }
        stop = clock();
        verify_ms += elapsed_ms(start, stop);

        if (mlen != SPX_MLEN || memcmp(m, mout, SPX_MLEN) != 0) {
            fprintf(stderr, "message recovery failed\n");
            return 1;
        }
    }

    printf("RESULT,%d,%d,%d,%d,%d,%.3f,%.3f,%.3f\n",
           SPX_BYTES,
           SPX_PK_BYTES,
           SPX_SK_BYTES,
           SPX_MLEN,
           SPX_BENCH_ITERS,
           keygen_ms / SPX_BENCH_ITERS,
           sign_ms / SPX_BENCH_ITERS,
           verify_ms / SPX_BENCH_ITERS);

    free(m);
    free(sm);
    free(mout);
    return 0;
}
