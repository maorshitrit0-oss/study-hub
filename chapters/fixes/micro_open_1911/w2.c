#include <stdio.h>
#include <stdint.h>
/* bits 0-3: age, bit 4: happy, bits 5-7: size */
#define AGE_MASK   0x0F
#define HAPPY_MASK 0x10
#define SIZE_SHIFT 5
typedef struct { uint8_t data; } dog_t;
void dog_set_age_bug(dog_t *d, uint8_t age) { d->data |= age; }
void dog_set_age(dog_t *d, uint8_t age) { d->data = (d->data & ~AGE_MASK) | (age & AGE_MASK); }
void dog_set_happy(dog_t *d, int h) { if (h) d->data |= HAPPY_MASK; else d->data &= ~HAPPY_MASK; }
uint8_t dog_get_size(dog_t *d) { return d->data >> SIZE_SHIFT; }
int main(void) {
    dog_t d = { 0x00 };
    d.data |= (3 << SIZE_SHIFT);
    dog_set_age_bug(&d, 9);
    dog_set_happy(&d, 1);
    printf("a: 0x%02X\n", d.data);
    dog_set_age_bug(&d, 6);
    printf("b: 0x%02X age=%d\n", d.data, d.data & AGE_MASK);
    dog_set_age(&d, 6);
    printf("c: 0x%02X age=%d size=%d\n", d.data, d.data & AGE_MASK, dog_get_size(&d));
    return 0;
}
