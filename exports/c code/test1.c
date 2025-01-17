
#include <stdint.h>

float b[] = { 1, -1 };
float a[] = { 1, -0.5 };
float w[2] = {0};

void filter_init() {
    for (int i = 0; i < 2; i++) w[i] = 0.0f;
}

float filter_process(float x) {
    float y = 0.0f;
    w[0] = x - a[1] * w[1];
    y = b[0] * w[0] + b[1] * w[1];
    w[1] = w[0];
    return y;
}
