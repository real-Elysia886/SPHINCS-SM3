/*
This code was taken from the SPHINCS reference implementation and is public domain.
*/

#include "randombytes.h"

#ifdef _WIN32
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt")
#else
#include <errno.h>
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
            Sleep(1);
            continue;
        }
        x += chunk;
        xlen -= chunk;
    }
#else
    size_t request;
    ssize_t received;

    while (xlen > 0) {
        while (fd == -1) {
            fd = open("/dev/urandom", O_RDONLY);
            if (fd == -1) {
                sleep(1);
            }
        }

        request = xlen < 1048576 ? (size_t)xlen : (size_t)1048576;
        received = read(fd, x, request);
        if (received < 0) {
            if (errno == EINTR) {
                continue;
            }
            close(fd);
            fd = -1;
            sleep(1);
            continue;
        }
        if (received == 0) {
            close(fd);
            fd = -1;
            sleep(1);
            continue;
        }

        x += (size_t)received;
        xlen -= (unsigned long long)received;
    }
#endif
}
