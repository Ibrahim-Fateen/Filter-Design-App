
#include "digital_filter.h"

static const float bandpass_num0[] = {0.5f, 0.5f};static const float bandpass_den0[] = {-0.5f};
static const float bandpass_num1[] = {0.6f, 0.4f};static const float bandpass_den1[] = {-0.3f};
void bandpass_init(bandpass_filter_t* f) {
    for(int s = 0; s < 2; s++) {
        for(int i = 0; i < 1; i++) {
            f->state[s][i] = 0.0f;
        }
    }
    f->output = 0.0f;
}

float bandpass_process(bandpass_filter_t* f, float input) {
    float section_input = input;

    
    // Section 0
    float new_state0 = section_input;
    for(int i = 0; i < 1; i++) {
        new_state0 -= bandpass_den0[i] * f->state[0][i];
    }

    section_input = bandpass_num0[0] * new_state0;
    for(int i = 0; i < 1; i++) {
        section_input += bandpass_num0[i + 1] * f->state[0][i];
    }

    for(int i = 0; i > 0; i--) {
        f->state[0][i] = f->state[0][i-1];
    }
    f->state[0][0] = new_state0;
 
    // Section 1
    float new_state1 = section_input;
    for(int i = 0; i < 1; i++) {
        new_state1 -= bandpass_den1[i] * f->state[1][i];
    }

    section_input = bandpass_num1[0] * new_state1;
    for(int i = 0; i < 1; i++) {
        section_input += bandpass_num1[i + 1] * f->state[1][i];
    }

    for(int i = 0; i > 0; i--) {
        f->state[1][i] = f->state[1][i-1];
    }
    f->state[1][0] = new_state1;


    f->output = section_input;
    return f->output;
}

