import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QMessageBox

from Filter import Filter
from PlotsWidget import FilterPlotsWidget
from ZPlaneWidget import ZPlaneWidget
from ElementsListWidget import ElementsListWidget
from FilterVisualizer import FilterVisualizer
from FilterCodeGenerator import FilterCodeGenerator


class FilterExportWidget(QWidget):
    def __init__(self, filter):
        super().__init__()
        self.filter_realizer = FilterVisualizer(filter)
        self.code_generator = FilterCodeGenerator(filter)
        self.filter = filter

        self.cascade_button = QPushButton("Show Cascade Form")
        self.direct_form_ii_button = QPushButton("Show Direct Form II")
        self.c_code_button = QPushButton("Generate C Code")
        self.add_all_pass_button = QPushButton("Add All-Pass Filter")

        self.cascade_button.clicked.connect(self.show_cascade)
        self.direct_form_ii_button.clicked.connect(self.show_direct_form_ii)
        self.c_code_button.clicked.connect(self.generate_c_code)
        self.add_all_pass_button.clicked.connect(self.show_all_pass_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.cascade_button)
        layout.addWidget(self.direct_form_ii_button)
        layout.addWidget(self.c_code_button)
        layout.addWidget(self.add_all_pass_button)
        self.setLayout(layout)

    def show_cascade(self):
        try:
            self.filter_realizer.draw_cascade_form()
        except ValueError as e:
            response = QMessageBox.question(
                self,
                "Filter Not Realizable",
                f"{str(e)}\n\nDo you want to auto-realize the filter?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                self.filter.auto_realize_filter()
                self.filter_realizer.draw_cascade_form()
            else:
                return
        self.filter_realizer.show()

    def show_direct_form_ii(self):
        try:
            self.filter_realizer.draw_direct_form_2()
        except ValueError as e:
            response = QMessageBox.question(
                self,
                "Filter Not Realizable",
                f"{str(e)}\n\nDo you want to auto-realize the filter?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                self.filter.auto_realize_filter()
                self.filter_realizer.draw_direct_form_2()
            else:
                return
        self.filter_realizer.show()

    def generate_c_code(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save C Code",
            "",
            "C Source Files (*.c);;All Files (*.*)"
        )
        
        if file_path:
            try:
                header_path, source_path = self.code_generator.export_c_code(file_path)
            except ValueError as e:
                response = QMessageBox.question(
                    self,
                    "Filter Not Realizable",
                    f"{str(e)}\n\nDo you want to auto-realize the filter?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.Yes:
                    self.filter.auto_realize_filter()
                    header_path, source_path = self.code_generator.export_c_code(file_path)
                else:
                    return
            except Exception as e:
                # Show error message if something goes wrong
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to generate code: {str(e)}"
                )
                return
            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Filter code generated successfully!\n\n"
                f"Header file: {header_path}\n"
                f"Source file: {source_path}"
            )

    def show_all_pass_dialog(self):
        pass


if __name__ == '__main__':
    app = QApplication()

    # Create filter and widgets
    filter = Filter()
    zplane = ZPlaneWidget()
    plots = FilterPlotsWidget()
    elements_list = ElementsListWidget()
    realizer_widget = FilterExportWidget(filter)

    zplane.set_filter(filter)
    plots.set_filter(filter)
    elements_list.set_filter(filter)

    # Show widgets
    zplane.show()
    plots.show()
    elements_list.show()
    realizer_widget.show()

    app.exec()
