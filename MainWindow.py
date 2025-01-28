from PySide6.QtWidgets import (QMainWindow, QWidget, QTabWidget, QVBoxLayout, 
                              QHBoxLayout, QMenuBar, QMenu, QFileDialog, QSplitter,
                              QMessageBox)
from PySide6.QtCore import Qt
import matplotlib.pyplot as plt

from Filter import Filter
from PlotsWidget import FilterPlotsWidget
from ZPlaneWidget import ZPlaneWidget
from ElementsListWidget import ElementsListWidget
from FilterUsageWidget import FilterUsageWidget
from AllPassFilter import AllPassFiltersListWidget
from FilterVisualizer import FilterVisualizer
from FilterCodeGenerator import FilterCodeGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Filter Designer")
        self.setMinimumSize(1200, 800)
        self.showMaximized()
        
        # Load and apply styles
        with open("styles.qss", "r") as f:
            self.setStyleSheet(f.read())
        
        # Create filter instance and helper classes
        self.filter = Filter()
        self.filter_realizer = FilterVisualizer(self.filter)
        self.code_generator = FilterCodeGenerator(self.filter)
        
        self.setup_ui()
        self.setup_menu_bar()

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)  # Connect tab change signal
        
        # Create and setup design tab
        design_tab = QWidget()
        design_layout = QHBoxLayout(design_tab)
        
        # Left side (Elements and All-Pass)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Create widgets
        self.elements_list = ElementsListWidget()
        self.all_pass_widget = AllPassFiltersListWidget()
        
        left_layout.addWidget(self.elements_list)
        left_layout.addWidget(self.all_pass_widget)
        
        # Right side (Z-Plane and Plots)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.zplane_widget = ZPlaneWidget()
        self.plots_widget = FilterPlotsWidget()
        
        right_layout.addWidget(self.zplane_widget)
        right_layout.addWidget(self.plots_widget)
        
        # Add panels to design tab
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        design_layout.addWidget(splitter)
        
        # Create and setup usage tab
        self.usage_widget = FilterUsageWidget()
        
        # Add tabs
        self.tab_widget.addTab(design_tab, "Filter Design")
        self.tab_widget.addTab(self.usage_widget, "Filter Usage")
        
        main_layout.addWidget(self.tab_widget)
        
        # Connect widgets to filter
        self.elements_list.set_filter(self.filter)
        self.all_pass_widget.set_filter(self.filter)
        self.zplane_widget.set_filter(self.filter)
        self.plots_widget.set_filter(self.filter)
        self.usage_widget.setFilter(self.filter)
        
    def setup_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Import submenu
        import_menu = QMenu("Import Filter", self)
        file_menu.addMenu(import_menu)
        
        # Import from file action
        import_file_action = import_menu.addAction("From File...")
        import_file_action.triggered.connect(self.import_filter_from_file)
        
        # Well-known filters submenu
        well_known_menu = import_menu.addMenu("Well-known Filters")
        
        # Add some example filters
        butterworth_action = well_known_menu.addAction("Butterworth Low-Pass")
        chebyshev_action = well_known_menu.addAction("Chebyshev Low-Pass")
        elliptic_action = well_known_menu.addAction("Elliptic Low-Pass")
        
        # Connect actions
        butterworth_action.triggered.connect(lambda: self.import_well_known_filter("butterworth"))
        chebyshev_action.triggered.connect(lambda: self.import_well_known_filter("chebyshev"))
        elliptic_action.triggered.connect(lambda: self.import_well_known_filter("elliptic"))
        
        # Export menu (moved below File menu)
        export_menu = QMenu("Export", self)
        file_menu.addMenu(export_menu)
        
        # Block diagram submenu
        block_diagram_menu = export_menu.addMenu("Block Diagram")
        
        # Add block diagram options
        cascade_action = block_diagram_menu.addAction("Cascade Form")
        direct_form_action = block_diagram_menu.addAction("Direct Form II")
        
        # C Code export action
        c_code_action = export_menu.addAction("Generate C Code")
        
        # Filter export action
        export_menu.addSeparator()  # Add separator line
        save_filter_action = export_menu.addAction("Save Filter...")
        
        # Connect export actions
        cascade_action.triggered.connect(self.show_cascade_form)
        direct_form_action.triggered.connect(self.show_direct_form)
        c_code_action.triggered.connect(self.generate_c_code)
        save_filter_action.triggered.connect(self.save_filter)
    
    def on_tab_changed(self, index):
        # If switching to Filter Usage tab (index 1)
        if index == 1:
            if not self.filter.is_realizable():
                response = QMessageBox.question(
                    self,
                    "Filter Not Realizable",
                    f"Do you want to auto-realize the filter?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.Yes:
                    self.filter.auto_realize_filter()
                else:
                    # Switch back to design tab
                    self.tab_widget.setCurrentIndex(0)
                    return

    def show_cascade_form(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Cascade Form Diagram",
            "",
            "PNG Files (*.png);;All Files (*.*)"
        )
        if not file_path:
            return

        try:
            fig = self.filter_realizer.draw_cascade_form()
            fig.savefig(file_path, bbox_inches='tight', dpi=300)
            plt.close(fig)
            QMessageBox.information(
                self,
                "Success",
                "Cascade form diagram saved successfully!"
            )
        except ValueError as e:
            response = QMessageBox.question(
                self,
                "Filter Not Realizable",
                f"{str(e)}\n\nDo you want to auto-realize the filter?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                self.filter.auto_realize_filter()
                fig = self.filter_realizer.draw_cascade_form()
                fig.savefig(file_path, bbox_inches='tight', dpi=300)
                plt.close(fig)
                QMessageBox.information(
                    self,
                    "Success",
                    "Cascade form diagram saved successfully!"
                )
            else:
                return

    def show_direct_form(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Direct Form II Diagram",
            "",
            "PNG Files (*.png);;All Files (*.*)"
        )
        if not file_path:
            return

        try:
            fig = self.filter_realizer.draw_direct_form_2()
            fig.savefig(file_path, bbox_inches='tight', dpi=300)
            plt.close(fig)
            QMessageBox.information(
                self,
                "Success",
                "Direct form II diagram saved successfully!"
            )
        except ValueError as e:
            response = QMessageBox.question(
                self,
                "Filter Not Realizable",
                f"{str(e)}\n\nDo you want to auto-realize the filter?",
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                self.filter.auto_realize_filter()
                fig = self.filter_realizer.draw_direct_form_2()
                fig.savefig(file_path, bbox_inches='tight', dpi=300)
                plt.close(fig)
                QMessageBox.information(
                    self,
                    "Success",
                    "Direct form II diagram saved successfully!"
                )
            else:
                return

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
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to generate code: {str(e)}"
                )
                return
            
            QMessageBox.information(
                self,
                "Success",
                f"Filter code generated successfully!\n\n"
                f"Header file: {header_path}\n"
                f"Source file: {source_path}"
            )

    def import_filter_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Filter",
            "",
            "Filter Files (*.dsp);;All Files (*.*)"
        )
        if file_path:
            try:
                self.filter.load_from_file(file_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to import filter: {str(e)}"
                )
            
    def import_well_known_filter(self, filter_type):
        # TODO: Implement well-known filter import
        pass

    def save_filter(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Filter",
            "",
            "Digital Filter Files (*.dsp);;All Files (*.*)"
        )
        if not file_path:
            return

        try:
            self.filter.save_to_file(file_path)
            QMessageBox.information(
                self,
                "Success",
                "Filter saved successfully!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save filter: {str(e)}"
            )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
