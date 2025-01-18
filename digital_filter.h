
/* Auto-generated filter implementation
 * Generated on: 2025-01-18 16:44:36
 * Filter type: Direct Form II
 * Filter order: N/A
 */

#ifndef DIGITAL_FILTER_H
#define DIGITAL_FILTER_H

#include <stdint.h>


typedef struct {
    float state[1];  // Delay line
    float output;          // Latest output
} lowpass_filter_t;



void lowpass_init(lowpass_filter_t* f);
float lowpass_process(lowpass_filter_t* f, float input);


#endif /* DIGITAL_FILTER_H */
