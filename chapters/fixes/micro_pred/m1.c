#include <stdio.h>
#include <stdint.h>

int main(void) {
    uint8_t r = 0xB6;                                   /* 1011 0110 */
    uint8_t a = r ^ 0x0F;                               /* toggle the low nibble */
    uint8_t b = r & (uint8_t)~(1U << 2);                /* clear bit 2 */
    uint8_t c = (r >> 4) & 0x3;                         /* bits 4-5 */
    uint8_t d = (r & (uint8_t)~(0x7 << 3)) | (5 << 3);  /* field bits 3-5 = 5 */
    printf("0x%02X 0x%02X %u 0x%02X\n", a, b, c, d);
    return 0;
}
