class FilterCodeGenerator:
    def __init__(self):
        self.header_template = """
/* Auto-generated filter implementation
 * Generated on: {timestamp}
 * Filter type: {filter_type}
 * Filter order: {order}
 */

#ifndef {header_guard}
#define {header_guard}

#include <stdint.h>

{struct_definitions}

{function_declarations}

#endif /* {header_guard} */
"""

        self.source_template = """
#include "{header_name}"

{function_definitions}
"""

    def generate_direct_form_2(self, name, denominator_coeffs, numerator_coeffs):
        """Generate C code for Direct Form II implementation"""
        order = max(len(denominator_coeffs), len(numerator_coeffs)) - 1

        # Generate structure definition
        struct_def = f"""
typedef struct {{
    float state[{order}];  // Delay line
    float output;          // Latest output
}} {name}_filter_t;
"""

        # Generate initialization function
        init_func = f"""
void {name}_init({name}_filter_t* f) {{
    for(int i = 0; i < {order}; i++) {{
        f->state[i] = 0.0f;
    }}
    f->output = 0.0f;
}}
"""

        # Generate coefficient arrays
        coeff_arrays = f"""
// Filter coefficients
static const float {name}_num[] = {{{', '.join([f"{x}f" for x in numerator_coeffs])}}};
static const float {name}_den[] = {{{', '.join([f"{x}f" for x in denominator_coeffs[1:]])}}};  // Skip a0
"""

        # Generate processing function
        process_func = f"""
float {name}_process({name}_filter_t* f, float input) {{
    float new_state = input;

    // Apply feedback
    for(int i = 0; i < {order}; i++) {{
        new_state -= {name}_den[i] * f->state[i];
    }}

    // Calculate output
    float output = {name}_num[0] * new_state;
    for(int i = 0; i < {order}; i++) {{
        output += {name}_num[i + 1] * f->state[i];
    }}

    // Update state
    for(int i = {order - 1}; i > 0; i--) {{
        f->state[i] = f->state[i-1];
    }}
    f->state[0] = new_state;
    f->output = output;

    return output;
}}
"""

        return {
            'struct_definitions': struct_def,
            'function_declarations': f"""
void {name}_init({name}_filter_t* f);
float {name}_process({name}_filter_t* f, float input);
""",
            'function_definitions': coeff_arrays + init_func + process_func
        }

    def generate_cascade_form(self, name, sections):
        """Generate C code for Cascade Form implementation"""
        total_sections = len(sections)
        max_order = max(max(len(d), len(n)) - 1 for d, n in sections)

        # Generate structure definition
        struct_def = f"""
typedef struct {{
    float state[{total_sections}][{max_order}];  // State for each section
    float output;                                // Latest output
}} {name}_filter_t;
"""

        # Generate initialization function
        init_func = f"""
void {name}_init({name}_filter_t* f) {{
    for(int s = 0; s < {total_sections}; s++) {{
        for(int i = 0; i < {max_order}; i++) {{
            f->state[s][i] = 0.0f;
        }}
    }}
    f->output = 0.0f;
}}
"""

        # Generate coefficient arrays for each section
        coeff_arrays = []
        for i, (deno, num) in enumerate(sections):
            coeff_arrays.extend([
                f"static const float {name}_num{i}[] = {{{', '.join([f'{x}f' for x in num])}}};"
                f"static const float {name}_den{i}[] = {{{', '.join([f'{x}f' for x in deno[1:]])}}};"
            ])
        coeff_arrays = "\n".join(coeff_arrays)

        # Generate processing function
        process_sections = []
        for i, (deno, num) in enumerate(sections):
            order = max(len(deno), len(num)) - 1
            section = f"""
    // Section {i}
    float new_state{i} = section_input;
    for(int i = 0; i < {order}; i++) {{
        new_state{i} -= {name}_den{i}[i] * f->state[{i}][i];
    }}

    section_input = {name}_num{i}[0] * new_state{i};
    for(int i = 0; i < {order}; i++) {{
        section_input += {name}_num{i}[i + 1] * f->state[{i}][i];
    }}

    for(int i = {order - 1}; i > 0; i--) {{
        f->state[{i}][i] = f->state[{i}][i-1];
    }}
    f->state[{i}][0] = new_state{i};
"""
            process_sections.append(section)

        process_func = f"""
float {name}_process({name}_filter_t* f, float input) {{
    float section_input = input;

    {' '.join(process_sections)}

    f->output = section_input;
    return f->output;
}}
"""

        return {
            'struct_definitions': struct_def,
            'function_declarations': f"""
void {name}_init({name}_filter_t* f);
float {name}_process({name}_filter_t* f, float input);
""",
            'function_definitions': coeff_arrays + init_func + process_func
        }

    def generate_files(self, name, filter_type, code_parts, timestamp, base_filename):
        """Generate header and source files

        Args:
            base_filename: The base filename without extension (e.g., 'myfilter')
        """
        # Create header guard from filename (e.g., MYFILTER_H)
        header_guard = f"{base_filename.upper()}_H"

        # Get just the filename without path for include statement
        header_name = f"{base_filename.split('/')[-1]}.h"

        header_content = self.header_template.format(
            timestamp=timestamp,
            filter_type=filter_type,
            order="N/A",
            header_guard=header_guard,
            struct_definitions=code_parts['struct_definitions'],
            function_declarations=code_parts['function_declarations']
        )

        source_content = self.source_template.format(
            header_name=header_name,
            function_definitions=code_parts['function_definitions']
        )

        return header_content, source_content