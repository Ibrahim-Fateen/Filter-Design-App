// test casc3 file
#include <stdio.h>
#include <math.h>
#include "casc3.h"

#define PI 3.14159265359f
#define SAMPLE_RATE 44100
#define TEST_DURATION_SEC 1
#define NUM_SAMPLES (TEST_DURATION_SEC * SAMPLE_RATE)

// Function to generate test signals
float generate_sine(float frequency, int sample_index) {
    return sinf(2.0f * PI * frequency * sample_index / SAMPLE_RATE);
}

void test_impulse_response(bandpass_filter_t* filter) {
    printf("\nTesting Impulse Response:\n");
    
    // Reset filter state
    bandpass_init(filter);
    
    // Apply impulse (1.0 followed by zeros)
    for(int i = 0; i < 10; i++) {
        float input = (i == 0) ? 1.0f : 0.0f;
        float output = bandpass_process(filter, input);
        printf("Sample %d: %f\n", i, output);
    }
}

void test_frequency_response(bandpass_filter_t* filter) {
    printf("\nTesting Frequency Response:\n");
    
    // Test frequencies (in Hz)
    float test_frequencies[] = {100.0f, 500.0f, 1000.0f, 2000.0f, 5000.0f};
    int num_frequencies = sizeof(test_frequencies) / sizeof(float);
    
    for(int freq_idx = 0; freq_idx < num_frequencies; freq_idx++) {
        float frequency = test_frequencies[freq_idx];
        float max_amplitude = 0.0f;
        
        // Reset filter state
        bandpass_init(filter);
        
        // Run sine wave through filter and find peak amplitude
        for(int i = 0; i < NUM_SAMPLES; i++) {
            float input = generate_sine(frequency, i);
            float output = bandpass_process(filter, input);
            float abs_output = fabsf(output);
            if(abs_output > max_amplitude) {
                max_amplitude = abs_output;
            }
        }
        
        printf("Frequency: %.1f Hz, Peak amplitude: %.4f\n", frequency, max_amplitude);
    }
}

void test_step_response(bandpass_filter_t* filter) {
    printf("\nTesting Step Response:\n");
    
    // Reset filter state
    bandpass_init(filter);
    
    // Apply step input (constant 1.0)
    for(int i = 0; i < 10; i++) {
        float output = bandpass_process(filter, 1.0f);
        printf("Sample %d: %f\n", i, output);
    }
}

int main() {
    bandpass_filter_t filter;
    
    // Test 1: Impulse Response
    test_impulse_response(&filter);
    
    // Test 2: Frequency Response
    test_frequency_response(&filter);
    
    // Test 3: Step Response
    test_step_response(&filter);
    
    return 0;
}