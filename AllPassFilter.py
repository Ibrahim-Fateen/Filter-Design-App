from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QListWidget, QComboBox, QSlider, QDoubleSpinBox
import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QDialog, QDialogButtonBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy import signal


class AllPassFiltersListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter = None
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
        w, _, phase_response = self.filter.get_frequency_response()
        dialog = AddAllPassFilterDialog(self, w, phase_response)
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
    def __init__(self, parent=None, w=None, phase_response=None):
        super().__init__(parent)
        self.setWindowTitle("Add All-Pass Filter")
        self.filter_phase_response = np.unwrap(phase_response)

        # Main layout
        layout = QVBoxLayout()

        # Preset filters combo box
        preset_layout = QHBoxLayout()
        self.preset_label = QLabel("Preset Filters:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Custom Filter",
            "90° Phase Shift (a=1.0, θ=π/2)",
            "180° Phase Shift (a=1.0, θ=π)",
            "45° Phase Shift (a=1.0, θ=π/4)"
        ])
        self.preset_combo.currentIndexChanged.connect(self.preset_selected)
        preset_layout.addWidget(self.preset_label)
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)

        # Radius (a) input
        radius_layout = QHBoxLayout()
        self.radius_label = QLabel("Pole radius (|a|):")
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(10, 1000)  # 0.1 to 10.0
        self.radius_slider.setValue(100)  # Default 1.0
        self.radius_slider.setTickInterval(10)
        self.radius_slider.setTickPosition(QSlider.TicksBelow)

        self.radius_spinbox = QDoubleSpinBox()
        self.radius_spinbox.setRange(0.1, 10.0)
        self.radius_spinbox.setValue(1.0)
        self.radius_spinbox.setSingleStep(0.1)
        self.radius_spinbox.setDecimals(3)

        radius_layout.addWidget(self.radius_label)
        radius_layout.addWidget(self.radius_slider)
        radius_layout.addWidget(self.radius_spinbox)
        layout.addLayout(radius_layout)

        # Angle (theta) input
        angle_layout = QHBoxLayout()
        self.angle_label = QLabel("Pole angle (θ):")
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 800)  # 0 to 2π * 127.32
        self.angle_slider.setValue(0)
        self.angle_slider.setTickInterval(100)  # π/4 intervals
        self.angle_slider.setTickPosition(QSlider.TicksBelow)

        self.angle_spinbox = QDoubleSpinBox()
        self.angle_spinbox.setRange(0, 2 * np.pi)
        self.angle_spinbox.setValue(0)
        self.angle_spinbox.setSingleStep(np.pi / 8)
        self.angle_spinbox.setDecimals(3)

        angle_layout.addWidget(self.angle_label)
        angle_layout.addWidget(self.angle_slider)
        angle_layout.addWidget(self.angle_spinbox)
        layout.addLayout(angle_layout)

        # Create plot
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Phase Response')
        self.ax.set_xlabel('ω (rad/sample)')
        self.ax.set_ylabel('Phase (rad)')
        self.ax.grid(True)
        layout.addWidget(self.canvas)

        # Add buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Connect signals
        self.radius_slider.valueChanged.connect(self.radius_slider_changed)
        self.radius_spinbox.valueChanged.connect(self.radius_spinbox_changed)
        self.angle_slider.valueChanged.connect(self.angle_slider_changed)
        self.angle_spinbox.valueChanged.connect(self.angle_spinbox_changed)

        self.setLayout(layout)
        self.update_plot()

    def radius_slider_changed(self, value):
        radius = value / 100.0
        self.radius_spinbox.blockSignals(True)
        self.radius_spinbox.setValue(radius)
        self.radius_spinbox.blockSignals(False)
        self.update_plot()

    def radius_spinbox_changed(self, value):
        slider_value = int(value * 100)
        self.radius_slider.blockSignals(True)
        self.radius_slider.setValue(slider_value)
        self.radius_slider.blockSignals(False)
        self.update_plot()

    def angle_slider_changed(self, value):
        angle = (value / 127.32) * (np.pi / 4)
        self.angle_spinbox.blockSignals(True)
        self.angle_spinbox.setValue(angle)
        self.angle_spinbox.blockSignals(False)
        self.update_plot()

    def angle_spinbox_changed(self, value):
        slider_value = int((value / (np.pi / 4)) * 127.32)
        self.angle_slider.blockSignals(True)
        self.angle_slider.setValue(slider_value)
        self.angle_slider.blockSignals(False)
        self.update_plot()

    def preset_selected(self, index):
        if index == 1:  # 90° Phase Shift
            self.radius_spinbox.setValue(1.0)
            self.angle_spinbox.setValue(np.pi / 2)
        elif index == 2:  # 180° Phase Shift
            self.radius_spinbox.setValue(1.0)
            self.angle_spinbox.setValue(np.pi)
        elif index == 3:  # 45° Phase Shift
            self.radius_spinbox.setValue(1.0)
            self.angle_spinbox.setValue(np.pi / 4)

    def update_plot(self):
        coefficient = self.radius_spinbox.value()
        angle = self.angle_spinbox.value()

        if coefficient == 0:
            return

        # Calculate the zero and pole
        zero = 1 / coefficient
        pole = coefficient

        # Adjust the zero and pole positions using the angle
        zero = zero * np.exp(1j * angle)
        pole = pole * np.exp(1j * angle)

        # Calculate the phase response of the inputted filter
        tf = signal.zpk2tf([zero], [pole], 1)
        w, h = signal.freqz(*tf, worN=1024)
        all_pass_phase = np.angle(h)
        all_pass_phase = np.unwrap(all_pass_phase)

        # Clear the plot
        self.ax.clear()
        self.ax.set_title('Phase Response')
        self.ax.set_xlabel('ω (rad/sample)')
        self.ax.set_ylabel('Phase (rad)')
        self.ax.grid(True)

        # Plot the phase response of the apf filter
        self.ax.plot(w, all_pass_phase, label='APF Filter', color='blue')  # blue solid line
        self.ax.plot(w, self.filter_phase_response, label='System Response', color='black')  # black solid line
        self.ax.plot(w, all_pass_phase + self.filter_phase_response, label='Combined Response', color='green', linestyle='--')

        self.ax.legend()
        self.canvas.draw()

    def get_coefficient(self):
        return self.radius_spinbox.value()

    def get_angle(self):
        return self.angle_spinbox.value()
