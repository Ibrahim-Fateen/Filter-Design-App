
#include "digital_filter.h"


// Filter coefficients
static const float lowpass_num[] = {0.5f, 0.5f};
static const float lowpass_den[] = {-0.5f};  // Skip a0

void lowpass_init(lowpass_filter_t* f) {
    for(int i = 0; i < 1; i++) {
        f->state[i] = 0.0f;
    }
    f->output = 0.0f;
}

float lowpass_process(lowpass_filter_t* f, float input) {
    float new_state = input;

    // Apply feedback
    for(int i = 0; i < 1; i++) {
        new_state -= lowpass_den[i] * f->state[i];
    }

    // Calculate output
    float output = lowpass_num[0] * new_state;
    for(int i = 0; i < 1; i++) {
        output += lowpass_num[i + 1] * f->state[i];
    }

    // Update state
    for(int i = 0; i > 0; i--) {
        f->state[i] = f->state[i-1];
    }
    f->state[0] = new_state;
    f->output = output;

    return output;
}

