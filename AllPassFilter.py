from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QFrame, QMessageBox, QLineEdit, QDialog, QDialogButtonBox
import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDialog, QDialogButtonBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import signal
from PlotsWidget import FilterPlotsWidget

class AllPassFiltersListWidget(QWidget):
    def __init__(self, parent=None, filter_instance=None, phase_response_instance=None):
        super().__init__(parent)
        self.filter = filter_instance
        self.phase_response = phase_response_instance
        self.setup_ui()
        self.setup_connections()

    def set_filter(self, filter_instance):
        """Connect to a filter instance"""
        self.filter = filter_instance
        self.filter.subscribe(self.update_from_filter, self)

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)

        # All-pass filters section
        apf_layout = QVBoxLayout()
        apf_header = QHBoxLayout()
        apf_label = QLabel("All-Pass Filters")
        self.clear_apf_btn = QPushButton("Clear All")
        apf_header.addWidget(apf_label)
        apf_header.addWidget(self.clear_apf_btn)
        self.apf_list = QListWidget()
        apf_layout.addLayout(apf_header)
        apf_layout.addWidget(self.apf_list)

        # Add button section
        add_layout = QHBoxLayout()
        self.add_apf_btn = QPushButton("Add All-Pass Filter")
        add_layout.addWidget(self.add_apf_btn)

        # Add everything to main layout
        main_layout.addLayout(apf_layout)
        main_layout.addLayout(add_layout)

    def setup_connections(self):
        self.clear_apf_btn.clicked.connect(self.clear_all)
        self.add_apf_btn.clicked.connect(self.show_add_apf_dialog)
        self.apf_list.itemDoubleClicked.connect(self.delete_apf)

    def update_from_filter(self, filter_instance):
        """Update the widget display from filter data"""
        self.apf_list.clear()
        for apf in filter_instance.all_pass_filters:
            self.apf_list.addItem(f"a: {apf['a']:.3f}, θ: {apf['theta']:.3f}")

    def notify_filter_change(self):
        """Update the filter with current widget data"""
        all_pass_filters = []
        for i in range(self.apf_list.count()):
            item_text = self.apf_list.item(i).text()
            a, theta = self.parse_apf(item_text)
            if a is not None and theta is not None:
                all_pass_filters.append({"a": a, "theta": theta})
        self.filter.update_all_pass_filters(all_pass_filters, self)

    def clear_all(self):
        self.apf_list.clear()
        self.notify_filter_change()

    def show_add_apf_dialog(self):
        dialog = AddAllPassFilterDialog(self, self.filter, self.phase_response)
        if dialog.exec():
            a = dialog.get_coefficient()
            theta = dialog.get_angle()
            if a is not None and theta is not None:
                self.apf_list.addItem(f"a: {a:.3f}, θ: {theta:.3f}")
                self.notify_filter_change()


    def delete_apf(self, item):
        """Delete the selected all-pass filter from the list and the filter instance."""

        # Now proceed with removing the filter from the system
        item_text = item.text()
        a, theta = self.parse_apf(item_text)
        if a is not None and theta is not None:
            # Remove the zero and pole corresponding to this all-pass filter
            zero = 1 / a
            pole = a
            angle_rad = np.deg2rad(theta)
            zero = zero * np.exp(1j * angle_rad)
            pole = pole * np.exp(1j * angle_rad)

            # Remove zero and pole from the filter system
            self.filter.remove_zero(zero)
            self.filter.remove_pole(pole)

            # Remove the all-pass filter from the all_pass_filters list
            self.filter.all_pass_filters = [
                apf for apf in self.filter.all_pass_filters
                if not (apf['a'] == a and apf['theta'] == theta)
            ]
            self.filter.notify_subscribers(self)

        # Get the row of the item and remove it from the list first
        row = self.apf_list.row(item)
        self.apf_list.takeItem(row)
        self.notify_filter_change()

    def parse_apf(self, text):
        """Parse all-pass filter from string"""
        try:
            parts = text.split(',')
            a = float(parts[0].split(':')[1].strip())
            theta = float(parts[1].split(':')[1].strip())
            return a, theta
        except (ValueError, IndexError):
            return None, None



class AddAllPassFilterDialog(QDialog):
    def __init__(self, parent=None, filter_instance=None, phase_response_instance=None):
        super().__init__(parent)
        self.setWindowTitle("Add All-Pass Filter")
        self.filter_instance = filter_instance
        self.phase_response_instance = phase_response_instance

        # Input the coefficient (a)
        self.coefficient_label = QLabel("Enter coefficient (a):")
        self.coefficient_input = QLineEdit()
        self.coefficient_input.textChanged.connect(self.update_plot)

        # Input the angle (theta)
        self.angle_label = QLabel("Enter angle (theta):")
        self.angle_input = QLineEdit()
        self.angle_input.textChanged.connect(self.update_plot)

        # Add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout setup
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.coefficient_label)
        input_layout.addWidget(self.coefficient_input)
        input_layout.addWidget(self.angle_label)
        input_layout.addWidget(self.angle_input)

        # Create plot
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Phase Response')
        self.ax.set_xlabel('ω (rad/sample)')
        self.ax.set_ylabel('Phase (rad)')
        self.ax.grid(True)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_coefficient(self):
        try:
            return float(self.coefficient_input.text())
        except ValueError:
            return None

    def get_angle(self):
        try:
            return float(self.angle_input.text())
        except ValueError:
            return None

    # def add_all_pass_filter_to_channel(self):
    #     a = self.get_coefficient()
    #     theta = self.get_angle()
    #     if a is not None and theta is not None:
    #         # Add the all-pass filter to the filter instance
    #         zero = 1 / a
    #         pole = a
    #         angle_rad = np.deg2rad(theta)
    #         zero = zero * np.exp(1j * angle_rad)
    #         pole = pole * np.exp(1j * angle_rad)
    #         self.filter_instance.add_zero(zero)
    #         self.filter_instance.add_pole(pole)
    #         self.filter_instance.notify_subscribers(self)
    #         self.accept()

    def update_plot(self):
        coefficient = self.get_coefficient()
        angle = self.get_angle()
        if coefficient is None or coefficient == 0 or angle is None:
            return

        # Calculate the zero and pole
        zero = 1 / coefficient
        pole = coefficient

        # Adjust the zero and pole positions using the angle
        angle_rad = np.deg2rad(angle)
        zero = zero * np.exp(1j * angle_rad)
        pole = pole * np.exp(1j * angle_rad)

        # Calculate the phase response of the inputted filter
        w, h = signal.freqz([zero], [pole], worN=1024)
        phase = np.angle(h)

        # Clear the plot
        self.ax.clear()
        self.ax.set_title('Phase Response')
        self.ax.set_xlabel('ω (rad/sample)')
        self.ax.set_ylabel('Phase (rad)')
        self.ax.grid(True)

        # Plot the phase response of the apf filter
        self.ax.plot(w, phase, label='APF Filter', color='blue')

        # Plot the original response of the existing filter system
        if self.filter_instance:
            system_w, system_magnitude_db, system_phase = self.filter_instance.get_frequency_response()
            self.ax.plot(system_w, system_phase, label='System Response', color='red')



        self.ax.legend()
        self.canvas.draw()


