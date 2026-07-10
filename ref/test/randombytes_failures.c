#include <errno.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#ifdef _WIN32

int main(void)
{
    printf("randombytes POSIX failure test skipped on Windows\n");
    return 0;
}

#else

#define open mock_open
#define read mock_read
#define close mock_close
#define sleep mock_sleep
#include "../randombytes.c"
#undef open
#undef read
#undef close
#undef sleep

static int open_calls;
static int read_calls;
static int close_calls;
static int sleep_calls;

int mock_open(const char *path, int flags, ...)
{
    (void)path;
    (void)flags;
    open_calls++;
    return 10 + open_calls;
}

ssize_t mock_read(int handle, void *buf, size_t len)
{
    (void)handle;
    read_calls++;
    if (read_calls == 1) {
        errno = EINTR;
        return -1;
    }
    if (read_calls == 2) {
        return 0;
    }
    if (read_calls == 3) {
        errno = EIO;
        return -1;
    }
    memset(buf, 0xa5, len);
    return (ssize_t)len;
}

int mock_close(int handle)
{
    (void)handle;
    close_calls++;
    return 0;
}

unsigned int mock_sleep(unsigned int seconds)
{
    (void)seconds;
    sleep_calls++;
    return 0;
}

int main(void)
{
    unsigned char output[32] = {0};
    size_t i;

    randombytes(output, sizeof(output));
    for (i = 0; i < sizeof(output); i++) {
        if (output[i] != 0xa5) {
            return 1;
        }
    }

    if (open_calls != 3 || read_calls != 4 ||
            close_calls != 2 || sleep_calls != 2) {
        return 1;
    }

    printf("randombytes failure recovery passed\n");
    return 0;
}

#endif
