from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QFrame, QMessageBox, QLineEdit, QDialog, QDialogButtonBox

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
        dialog = AddAllPassFilterDialog(self)
        if dialog.exec():
            a = dialog.get_coefficient()
            theta = dialog.get_angle()
            if a is not None and theta is not None:
                self.apf_list.addItem(f"a: {a:.3f}, θ: {theta:.3f}")
                self.notify_filter_change()

    def delete_apf(self, item):
        self.apf_list.takeItem(self.apf_list.row(item))
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add All-Pass Filter")

        # Input the coefficient (a)
        self.coefficient_label = QLabel("Enter coefficient (a):")
        self.coefficient_input = QLineEdit()

        # Input the angle (theta)
        self.angle_label = QLabel("Enter angle (theta):")
        self.angle_input = QLineEdit()

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

        layout = QVBoxLayout()
        layout.addLayout(input_layout)
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