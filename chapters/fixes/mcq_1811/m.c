#include <stdio.h>
#include <stdint.h>
#define AGE_BITS 5
#define MAX_AGE_BAD 1 << AGE_BITS - 1
#define MAX_AGE ((1 << AGE_BITS) - 1)
#define AGE_START_BIT 2
#define AGE_MASK (MAX_AGE << AGE_START_BIT)
#define HAPPY_MASK (1 << 1)
int dog_set_is_happy(unsigned char *dog, int status) { if (!dog) return -1; if (status) *dog |= HAPPY_MASK; else *dog &= ~HAPPY_MASK; return 0; }
int dog_set_age(unsigned char *dog, int new_age) { if (!dog || new_age < 0 || new_age > MAX_AGE) return -1; *dog &= ~AGE_MASK; *dog |= (unsigned char)(new_age << AGE_START_BIT); return 0; }
int main(void) {
    uint8_t reg = 0x5A; reg = (reg | 0x01) & ~0x08; printf("a 0x%02X\n", reg);
    uint8_t r2 = 0x5A; r2 = (r2 | 0x08) & ~0x01; printf("a2 0x%02X\n", r2);
    uint8_t dog = 0xB6; printf("age %d sex %d happy %d hungry %d\n", (dog >> 2) & 0x1F, (dog >> 7) & 1, (dog >> 1) & 1, dog & 1);
    uint8_t x = 0x05, mask = (uint8_t)(1U << 2); x ^= mask; printf("xor1 0x%02X ", x); x ^= mask; printf("xor2 0x%02X\n", x);
    printf("bad %d good %d mask 0x%02X\n", MAX_AGE_BAD, MAX_AGE, AGE_MASK);
    unsigned char d = 0x83; dog_set_is_happy(&d, 0); printf("happy0 0x%02X\n", d);
    unsigned char e = 0xFF; dog_set_age(&e, 5); printf("age5 0x%02X\n", e);
    unsigned char f = 0xFF; f |= (unsigned char)(5 << 2); printf("noclear 0x%02X\n", f);
    uint8_t y = 0x6D; y = (y & ~(1U << 2)) | (1U << 7); printf("q1 0x%02X\n", y);
    printf("adc %.4f mV, 10bit %.3f mV\n", 3.3/4096*1000, 3.3/1024*1000);
    return 0;
}
