import matplotlib.pyplot as plt
from PySide6.QtWidgets import QFileDialog, QApplication, QPushButton, QVBoxLayout, QWidget, QComboBox


def export_c_code(coefficients, structure="direct_form_ii"):
    file_name, _ = QFileDialog.getSaveFileName(None, "Save C Code", "", "C Files (*.c)")
    if not file_name:
        return

    c_code = ""
    if structure == "direct_form_ii":
        c_code = generate_direct_form_ii_code(coefficients)
    elif structure == "cascade":
        c_code = generate_cascade_code(coefficients)

    with open(file_name, 'w') as file:
        file.write(c_code)

def generate_direct_form_ii_code(coefficients):
    b, a = coefficients["numerator"], coefficients["denominator"]
    code = f"""
#include <stdint.h>

float b[] = {{ {', '.join(map(str, b))} }};
float a[] = {{ {', '.join(map(str, a))} }};
float w[{len(b)}] = {{0}};

void filter_init() {{
    for (int i = 0; i < {len(b)}; i++) w[i] = 0.0f;
}}

float filter_process(float x) {{
    float y = 0.0f;
    w[0] = x - a[1] * w[1];
    y = b[0] * w[0] + b[1] * w[1];
    w[1] = w[0];
    return y;
}}
"""
    print("Generated C code:")
    return code

def generate_cascade_code(coefficients):
    sections = coefficients["sections"]
    num_sections = len(sections)
    code = f"""
#include <stdint.h>

#define NUM_SECTIONS {num_sections}

float b[NUM_SECTIONS][3] = {{
    {',\n    '.join(['{' + ', '.join(map(str, section['b'])) + '}' for section in sections])}
}};

float a[NUM_SECTIONS][3] = {{
    {',\n    '.join(['{' + ', '.join(map(str, section['a'])) + '}' for section in sections])}
}};

float w[NUM_SECTIONS][2] = {{0}};

void filter_init() {{
    for (int i = 0; i < NUM_SECTIONS; i++) {{
        w[i][0] = 0.0f;
        w[i][1] = 0.0f;
    }}
}}

float filter_process(float x) {{
    for (int i = 0; i < NUM_SECTIONS; i++) {{
        float y = b[i][0] * x + w[i][0];
        w[i][0] = b[i][1] * x - a[i][1] * y + w[i][1];
        w[i][1] = b[i][2] * x - a[i][2] * y;
        x = y;
    }}
    return x;
}}
"""
    print("Generated C code:")
    return code

def export_filter_diagram(coefficients, structure="direct_form_ii"):
    file_name, _ = QFileDialog.getSaveFileName(None, "Save Diagram", "", "PNG Files (*.png)")
    if not file_name:
        return

    if structure == "direct_form_ii":
        plot_direct_form_ii(coefficients, file_name)
    elif structure == "cascade":
        plot_cascade(coefficients, file_name)
    print(f"Filter diagram saved to {file_name}")

def plot_direct_form_ii(coefficients, file_name):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.text(0.1, 0.5, "Input", fontsize=12)
    ax.text(0.4, 0.5, f"b0: {coefficients['numerator'][0]}", fontsize=12)
    ax.text(0.55, 0.5, f"b1: {coefficients['numerator'][1]}", fontsize=12)
    ax.text(0.7, 0.5, f"a1: {coefficients['denominator'][1]}", fontsize=12)
    ax.arrow(0.2, 0.5, 0.15, 0, head_width=0.02, head_length=0.02)
    ax.arrow(0.5, 0.5, 0.15, 0, head_width=0.02, head_length=0.02)
    ax.set_axis_off()
    plt.savefig(file_name)
    plt.close()

def plot_cascade(coefficients, file_name):
    fig, ax = plt.subplots(figsize=(12, 6))
    sections = coefficients.get("sections", [])
    for i, section in enumerate(sections):
        ax.text(0.1 + i * 0.3, 0.5, f"Biquad {i+1}\n b: {section['b']} \n a: {section['a']}",
                fontsize=10, bbox=dict(boxstyle="round", facecolor="wheat"))
        if i < len(sections) - 1:
            ax.arrow(0.1 + i * 0.3 + 0.15, 0.5, 0.15, 0, head_width=0.02, head_length=0.02)
    ax.set_axis_off()
    plt.savefig(file_name)
    plt.close()

# test code
cascade_coefficients = {
    "sections": [
        {"b": [1, -1, 0.5], "a": [1, -0.5, 0.25]},
        {"b": [1, -0.8, 0.3], "a": [1, -0.4, 0.1]}
    ]
}
direct_form_coeff = {"numerator": [1, -1], "denominator": [1, -0.5]}
app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
export_c_code_button = QPushButton("Export C Code")
# add export_filter_diagram combo box to choose the structure
export_filter_diagram_combobox = QComboBox()
export_filter_diagram_combobox.addItems(["cascade", "direct_form_ii"])
# add button to export the filter diagram
export_filter_diagram_button = QPushButton("Export Filter Diagram")
export_filter_diagram_button.clicked.connect(lambda: export_filter_diagram(cascade_coefficients, export_filter_diagram_combobox.currentText()))
export_c_code_button.clicked.connect(lambda: export_c_code({"numerator": [1, -1], "denominator": [1, -0.5]}))

layout.addWidget(export_filter_diagram_combobox)
layout.addWidget(export_filter_diagram_button)
layout.addWidget(export_c_code_button)
window.setLayout(layout)
window.show()
app.exec()