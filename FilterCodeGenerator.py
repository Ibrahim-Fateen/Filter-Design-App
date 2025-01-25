from datetime import datetime


class FilterCodeGenerator:
    def __init__(self, transfer_function):
        self.header_template = """
/* Auto-generated filter implementation
 * Generated on: {timestamp}
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
        self.tf = transfer_function
        self.header_path = None
        self.source_path = None

    def export_c_code(self, file_path, name="filter"):
        base_name = file_path.rsplit('.', 1)[0]
        base_filename = base_name.split('/')[-1]

        code_parts = self._generate_code_parts(name)
        header_content, source_content = self._get_files_content(
            code_parts,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            base_filename
        )

        self.header_path = f"{base_name}.h"
        self.source_path = f"{base_name}.c"
        self._write_files(header_content, source_content)
        return self.header_path, self.source_path

    def _generate_code_parts(self, name):
        denominator_coeffs = self.tf[1]
        numerator_coeffs = self.tf[0]
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

    def _get_files_content(self, code_parts, timestamp, base_filename):
        """Generate header and source files

        Args:
            base_filename: The base filename without extension (e.g., 'myfilter')
            code_parts: Dictionary containing struct definitions, function declarations, and function definitions
            timestamp: Timestamp for the code generation
            base_filename: Base filename for the generated files
        """
        # Create header guard from filename (e.g., MYFILTER_H)
        header_guard = f"{base_filename.upper()}_H"

        # Get just the filename without path for include statement
        header_name = f"{base_filename.split('/')[-1]}.h"

        header_content = self.header_template.format(
            timestamp=timestamp,
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

    def _write_files(self, header, source):
        """Write header and source files to disk"""
        with open(self.header_path, "w") as f:
            f.write(header)

        with open(self.source_path, "w") as f:
            f.write(source)

#     def generate_cascade_form(self, name, sections):
#         """Generate C code for Cascade Form implementation"""
#         total_sections = len(sections)
#         max_order = max(max(len(d), len(n)) - 1 for d, n in sections)
#
#         # Generate structure definition
#         struct_def = f"""
# typedef struct {{
#     float state[{total_sections}][{max_order}];  // State for each section
#     float output;                                // Latest output
# }} {name}_filter_t;
# """
#
#         # Generate initialization function
#         init_func = f"""
# void {name}_init({name}_filter_t* f) {{
#     for(int s = 0; s < {total_sections}; s++) {{
#         for(int i = 0; i < {max_order}; i++) {{
#             f->state[s][i] = 0.0f;
#         }}
#     }}
#     f->output = 0.0f;
# }}
# """
#
#         # Generate coefficient arrays for each section
#         coeff_arrays = []
#         for i, (deno, num) in enumerate(sections):
#             coeff_arrays.extend([
#                 f"static const float {name}_num{i}[] = {{{', '.join([f'{x}f' for x in num])}}};"
#                 f"static const float {name}_den{i}[] = {{{', '.join([f'{x}f' for x in deno[1:]])}}};"
#             ])
#         coeff_arrays = "\n".join(coeff_arrays)
#
#         # Generate processing function
#         process_sections = []
#         for i, (deno, num) in enumerate(sections):
#             order = max(len(deno), len(num)) - 1
#             section = f"""
#     // Section {i}
#     float new_state{i} = section_input;
#     for(int i = 0; i < {order}; i++) {{
#         new_state{i} -= {name}_den{i}[i] * f->state[{i}][i];
#     }}
#
#     section_input = {name}_num{i}[0] * new_state{i};
#     for(int i = 0; i < {order}; i++) {{
#         section_input += {name}_num{i}[i + 1] * f->state[{i}][i];
#     }}
#
#     for(int i = {order - 1}; i > 0; i--) {{
#         f->state[{i}][i] = f->state[{i}][i-1];
#     }}
#     f->state[{i}][0] = new_state{i};
# """
#             process_sections.append(section)
#
#         process_func = f"""
# float {name}_process({name}_filter_t* f, float input) {{
#     float section_input = input;
#
#     {' '.join(process_sections)}
#
#     f->output = section_input;
#     return f->output;
# }}
# """
#
#         return {
#             'struct_definitions': struct_def,
#             'function_declarations': f"""
# void {name}_init({name}_filter_t* f);
# float {name}_process({name}_filter_t* f, float input);
# """,
#             'function_definitions': coeff_arrays + init_func + process_func
#         }
