/*
This code was taken from the SPHINCS reference implementation and is public domain.
*/

#include "randombytes.h"

#ifdef _WIN32
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt")
#else
#include <fcntl.h>
#include <unistd.h>
#endif

#ifndef _WIN32
static int fd = -1;
#endif

void randombytes(unsigned char *x, unsigned long long xlen)
{
#ifdef _WIN32
    while (xlen > 0) {
        ULONG chunk = xlen > 1048576 ? 1048576 : (ULONG)xlen;
        if (BCryptGenRandom(NULL, x, chunk, BCRYPT_USE_SYSTEM_PREFERRED_RNG) != 0) {
            continue;
        }
        x += chunk;
        xlen -= chunk;
    }
#else
    unsigned long long i;

    if (fd == -1) {
        for (;;) {
            fd = open("/dev/urandom", O_RDONLY);
            if (fd != -1) {
                break;
            }
            sleep(1);
        }
    }

    while (xlen > 0) {
        if (xlen < 1048576) {
            i = xlen;
        }
        else {
            i = 1048576;
        }

        i = (unsigned long long)read(fd, x, i);
        if (i < 1) {
            sleep(1);
            continue;
        }

        x += i;
        xlen -= i;
    }
#endif
}
