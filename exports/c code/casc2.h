
/* Auto-generated filter implementation
 * Generated on: 2025-01-18 16:50:11
 * Filter type: Cascade Form
 * Filter order: N/A
 */

#ifndef DIGITAL_FILTER_H
#define DIGITAL_FILTER_H

#include <stdint.h>


typedef struct {
    float state[2][1];  // State for each section
    float output;                                // Latest output
} bandpass_filter_t;



void bandpass_init(bandpass_filter_t* f);
float bandpass_process(bandpass_filter_t* f, float input);


#endif /* DIGITAL_FILTER_H */
