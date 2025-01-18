
/* Auto-generated filter implementation
 * Generated on: 2025-01-18 17:39:52
 * Filter type: cascade
 * Filter order: N/A
 */

#ifndef CASC3_H
#define CASC3_H

#include <stdint.h>


typedef struct {
    float state[2][1];  // State for each section
    float output;                                // Latest output
} bandpass_filter_t;



void bandpass_init(bandpass_filter_t* f);
float bandpass_process(bandpass_filter_t* f, float input);


#endif /* CASC3_H */
