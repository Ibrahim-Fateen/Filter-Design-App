/******************************* SOURCE LICENSE *********************************
Copyright (c) 2021 MicroModeler.

A non-exclusive, nontransferable, perpetual, royalty-free license is granted to the Licensee to 
use the following Information for academic, non-profit, or government-sponsored research purposes.
Use of the following Information under this License is restricted to NON-COMMERCIAL PURPOSES ONLY.
Commercial use of the following Information requires a separately executed written license agreement.

This Information is distributed WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

******************************* END OF LICENSE *********************************/

// A commercial license for MicroModeler DSP can be obtained at https://www.micromodeler.com/launch.jsp

// Begin header file, filter1.h

#ifndef FILTER1_H_ // Include guards
#define FILTER1_H_

/*
Generated code is based on the following filter design:
<micro.DSP.FilterDocument sampleFrequency="#1" arithmetic="float" biquads="Direct1" classname="filter1" inputMax="#1" inputShift="#15" >
  <micro.DSP.IirButterworthFilter N="#4" bandType="l" w1="#0.1" w2="#0.4" stopbandRipple="#undefined" passbandRipple="#undefined" transitionRatio="#undefined" >
    <micro.DSP.FilterStructure coefficientBits="#0" variableBits="#0" accumulatorBits="#0" biquads="Direct1" >
      <micro.DSP.FilterSection form="Direct1" historyType="Double" accumulatorBits="#0" variableBits="#0" coefficientBits="#0" />
      <micro.DSP.FilterSection form="Direct1" historyType="Double" accumulatorBits="#0" variableBits="#0" coefficientBits="#0" />
    </micro.DSP.FilterStructure>
    <micro.DSP.PoleOrZeroContainer >
      <micro.DSP.PoleOrZero i="#0.4433234935749398" r="#0.6604567154097131" isPoint="#true" isPole="#true" isZero="#false" symmetry="c" N="#1" cascade="#1" />
      <micro.DSP.PoleOrZero i="#0.14577410495251691" r="#0.5242997881813058" isPoint="#true" isPole="#true" isZero="#false" symmetry="c" N="#1" cascade="#0" />
      <micro.DSP.PoleOrZero i="#0" r="#-1" isPoint="#true" isPole="#false" isZero="#true" symmetry="r" N="#1" cascade="#0" />
      <micro.DSP.PoleOrZero i="#0" r="#-1" isPoint="#true" isPole="#false" isZero="#true" symmetry="r" N="#1" cascade="#0" />
      <micro.DSP.PoleOrZero i="#0" r="#-1" isPoint="#true" isPole="#false" isZero="#true" symmetry="r" N="#1" cascade="#1" />
      <micro.DSP.PoleOrZero i="#0" r="#-1" isPoint="#true" isPole="#false" isZero="#true" symmetry="r" N="#1" cascade="#1" />
    </micro.DSP.PoleOrZeroContainer>
    <micro.DSP.GenericC.CodeGenerator generateTestCases="#false" />
    <micro.DSP.GainControl magnitude="#1" frequency="#0.0009765625" peak="#true" />
  </micro.DSP.IirButterworthFilter>
</micro.DSP.FilterDocument>

*/

static const int filter1_numStages = 2;
static const int filter1_coefficientLength = 10;
extern float filter1_coefficients[10];

typedef struct
{
	float state[8];
	float output;
} filter1Type;

typedef struct
{
    float *pInput;
    float *pOutput;
    float *pState;
    float *pCoefficients;
    short count;
} filter1_executionState;


filter1Type *filter1_create( void );
void filter1_destroy( filter1Type *pObject );
void filter1_init( filter1Type * pThis );
void filter1_reset( filter1Type * pThis );
#define filter1_writeInput( pThis, input )  \
    filter1_filterBlock( pThis, &(input), &(pThis)->output, 1 );

#define filter1_readOutput( pThis )  \
    (pThis)->output

int filter1_filterBlock( filter1Type * pThis, float * pInput, float * pOutput, unsigned int count );
#define filter1_outputToFloat( output )  \
    (output)

#define filter1_inputFromFloat( input )  \
    (input)

void filter1_filterBiquad( filter1_executionState * pExecState );
#endif // FILTER1_H_
	
