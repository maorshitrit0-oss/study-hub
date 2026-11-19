#include <stdio.h>
#include <stdint.h>
int main(void) {
    uint8_t x = 0xB4;
    x |= (1 << 1);
    printf("1: 0x%02X\n", x);
    x &= ~(1 << 4);
    printf("2: 0x%02X\n", x);
    x ^= 0x0F;
    printf("3: 0x%02X\n", x);
    if (x & (1 << 7)) printf("bit7 on\n"); else printf("bit7 off\n");
    printf("4: %d\n", (x >> 2) & 0x3);
    return 0;
}
