#include <stdio.h>
#include <stdint.h>

#define COLOR_BITS   2
#define SLEEP_BIT    2
#define WEIGHT_START 3
#define WEIGHT_BITS  5
#define COLOR_MASK   ((1 << COLOR_BITS) - 1)                          /* 0x03 */
#define SLEEP_MASK   (1 << SLEEP_BIT)                                 /* 0x04 */
#define MAX_WEIGHT   ((1 << WEIGHT_BITS) - 1)                         /* 31 */
#define WEIGHT_MASK  (MAX_WEIGHT << WEIGHT_START)                     /* 0xF8 */

int cat_get_weight(const uint8_t *cat) {
    if (!cat)
        return -1;
    return (*cat & WEIGHT_MASK) >> WEIGHT_START;
}

int cat_set_color(uint8_t *cat, int color) {
    if (!cat || color < 0 || color > COLOR_MASK)
        return -1;
    *cat = (*cat & (uint8_t)~COLOR_MASK) | (uint8_t)color;
    return 0;
}

int main(void) {
    uint8_t cat = 0x5D;                  /* 0101 1101 */
    printf("weight=%d color=%d sleeping=%d\n", cat_get_weight(&cat), cat & COLOR_MASK, (cat & SLEEP_MASK) != 0);
    int rc = cat_set_color(&cat, 2);
    printf("rc=%d cat=0x%02X\n", rc, cat);
    printf("rc=%d cat=0x%02X\n", cat_set_color(&cat, 4), cat);
    return 0;
}
