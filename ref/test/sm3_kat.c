#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "../sm3.h"

static void hex_to_bytes(uint8_t *out, const char *hex)
{
    size_t i;

    for (i = 0; hex[2 * i] != '\0'; i++) {
        uint8_t hi = (uint8_t)(hex[2 * i] <= '9'
            ? hex[2 * i] - '0'
            : hex[2 * i] - 'A' + 10);
        uint8_t lo = (uint8_t)(hex[2 * i + 1] <= '9'
            ? hex[2 * i + 1] - '0'
            : hex[2 * i + 1] - 'A' + 10);
        out[i] = (uint8_t)((hi << 4) | lo);
    }
}

static int check_vector(const char *name, const uint8_t *msg, size_t msglen,
                        const char *expected_hex)
{
    uint8_t got[SPX_SM3_OUTPUT_BYTES];
    uint8_t expected[SPX_SM3_OUTPUT_BYTES];

    hex_to_bytes(expected, expected_hex);
    sm3(got, msg, msglen);

    if (memcmp(got, expected, SPX_SM3_OUTPUT_BYTES) != 0) {
        printf("SM3 KAT failed: %s\n", name);
        return -1;
    }

    printf("SM3 KAT passed: %s\n", name);
    return 0;
}

int main(void)
{
    int ret = 0;
    const uint8_t abc[] = {'a', 'b', 'c'};
    const uint8_t block64[] =
        "abcdabcdabcdabcdabcdabcdabcdabcd"
        "abcdabcdabcdabcdabcdabcdabcdabcd";

    ret |= check_vector(
        "empty",
        (const uint8_t *)"",
        0,
        "1AB21D8355CFA17F8E61194831E81A8F22BEC8C728FEFB747ED035EB5082AA2B");

    ret |= check_vector(
        "abc",
        abc,
        sizeof(abc),
        "66C7F0F462EEEDD9D1F2D46BDC10E4E24167C4875CF2F7A2297DA02B8F4BA8E0");

    ret |= check_vector(
        "abcd x 16",
        block64,
        sizeof(block64) - 1,
        "DEBE9FF92275B8A138604889C18E5A4D6FDB70E5387E5765293DCBA39C0C5732");

    return ret == 0 ? 0 : 1;
}
