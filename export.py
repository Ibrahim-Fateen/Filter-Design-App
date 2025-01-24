import matplotlib.pyplot as plt
from PySide6.QtWidgets import QFileDialog, QApplication, QPushButton, QVBoxLayout, QWidget, QComboBox
from datetime import datetime
import os

from FilterRealizer import FilterRealizer
from filter_code_generator import FilterCodeGenerator

visualizer = FilterRealizer()
code_generator = FilterCodeGenerator()


def export_c_code(name="filter", denominator=None, numerator=None, sections=None, structure="direct_form_ii"):
    file_name, _ = QFileDialog.getSaveFileName(None, "Save C Code", "", "C Files (*.c)")
    if not file_name:
        return

    # Remove extension and get base name
    base_name = file_name.rsplit('.', 1)[0]
    base_filename = base_name.split('/')[-1]  # Get filename without path

    # Generate code parts based on structure
    if structure == "direct_form_ii":
        code_parts = code_generator.generate_direct_form_2(name, denominator, numerator)
    elif structure == "cascade":
        code_parts = code_generator.generate_cascade_form(name, sections)

    # Generate files with proper naming
    header, source = code_generator.generate_files(
        name,
        structure,
        code_parts,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        base_filename
    )

    # Save header file
    header_path = f"{base_name}.h"
    with open(header_path, "w") as f:
        f.write(header)

    # Save source file
    source_path = f"{base_name}.c"
    with open(source_path, "w") as f:
        f.write(source)

    return header_path, source_path

def generate_direct_form_ii_code(name, denominator, numerator):
    code_parts = code_generator.generate_direct_form_2(name, denominator, numerator)
    header, source = code_generator.generate_files(
        name,
        "Direct Form II",
        code_parts,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return header, source

def generate_cascade_code(name, sections):
    code_parts = code_generator.generate_cascade_form(name, sections)
    header, source = code_generator.generate_files(
        name,
        "Cascade Form",
        code_parts,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    return header, source


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
    visualizer.draw_direct_form_2(coefficients["denominator"], coefficients["numerator"])
    plt.savefig(file_name)
    plt.close()

def plot_cascade(coefficients, file_name):
    visualizer.draw_cascade_form(coefficients["sections"])
    plt.savefig(file_name)
    plt.close()

# test code
cascade_coefficients = {"sections" : [
    ([0.2, 0.1], [1.0, 0.4, 0.2]),  # First section
    ([0.1], [1.0, 0.3]),  # Second section
    ([0.15], [1.0, 0.25])  # Third section
]
}

direct_form_coeff = {"numerator": [1, -1], "denominator": [1, -0.5]}

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
export_cascade_code_button = QPushButton("Export cascade C Code")
export_direct_form_ii_code_button = QPushButton("Export direct form II C Code")
# add export_filter_diagram combo box to choose the structure
export_filter_diagram_combobox = QComboBox()
export_filter_diagram_combobox.addItems(["cascade", "direct_form_ii"])
# add button to export the filter diagram
export_filter_diagram_button = QPushButton("Export Filter Diagram")
export_filter_diagram_button.clicked.connect(lambda: export_filter_diagram(direct_form_coeff, export_filter_diagram_combobox.currentText()))

export_cascade_code_button.clicked.connect(lambda: export_c_code(name = "bandpass", sections = [
    ([1.0, -0.5], [0.5, 0.5]),  # First section coefficients
    ([1.0, -0.3], [0.6, 0.4])   # Second section coefficients
], structure="cascade"))
export_direct_form_ii_code_button.clicked.connect(lambda: export_c_code(name = "lowpass", denominator = [1.0, -0.5], numerator = [0.5, 0.5], structure="direct_form_ii"))

layout.addWidget(export_filter_diagram_combobox)
layout.addWidget(export_filter_diagram_button)
layout.addWidget(export_cascade_code_button)
layout.addWidget(export_direct_form_ii_code_button)
window.setLayout(layout)
window.show()
app.exec()


# Example 1: Direct Form II filter
name = "lowpass"
denominator = [1.0, -0.5]  # a0, a1
numerator = [0.5, 0.5]     # b0, b1


# Example 2: Cascade Form filter
name = "bandpass"
sections = [
    ([1.0, -0.5], [0.5, 0.5]),  # First section coefficients
    ([1.0, -0.3], [0.6, 0.4])   # Second section coefficients
]

