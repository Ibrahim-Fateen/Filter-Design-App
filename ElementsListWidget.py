from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFrame
)
import cmath
import numpy as np


class ElementsListWidget(QWidget):
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

        # Top section with lists and swap button
        lists_section = QHBoxLayout()

        # Zeros section
        zeros_layout = QVBoxLayout()
        zeros_header = QHBoxLayout()
        zeros_label = QLabel("Zeros")
        self.clear_zeros_btn = QPushButton("Clear")
        zeros_header.addWidget(zeros_label)
        zeros_header.addWidget(self.clear_zeros_btn)
        self.zeros_list = QListWidget()
        zeros_layout.addLayout(zeros_header)
        zeros_layout.addWidget(self.zeros_list)

        # Swap button section
        swap_layout = QVBoxLayout()
        swap_layout.addStretch()
        self.swap_btn = QPushButton("⇄")
        swap_layout.addWidget(self.swap_btn)
        swap_layout.addStretch()

        # Poles section
        poles_layout = QVBoxLayout()
        poles_header = QHBoxLayout()
        poles_label = QLabel("Poles")
        self.clear_poles_btn = QPushButton("Clear")
        poles_header.addWidget(poles_label)
        poles_header.addWidget(self.clear_poles_btn)
        self.poles_list = QListWidget()
        poles_layout.addLayout(poles_header)
        poles_layout.addWidget(self.poles_list)

        # Add all sections to lists section
        lists_section.addLayout(zeros_layout)
        lists_section.addLayout(swap_layout)
        lists_section.addLayout(poles_layout)

        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        # Clear all button at the bottom
        self.clear_all_btn = QPushButton("Clear All")

        # Add everything to main layout
        main_layout.addLayout(lists_section)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.clear_all_btn)

        # Style the swap button
        self.swap_btn.setFixedWidth(40)

    def setup_connections(self):
        self.clear_zeros_btn.clicked.connect(self.clear_zeros)
        self.clear_poles_btn.clicked.connect(self.clear_poles)
        self.clear_all_btn.clicked.connect(self.clear_all)
        self.swap_btn.clicked.connect(self.swap_all)

        self.zeros_list.itemDoubleClicked.connect(self.delete_zero)
        self.poles_list.itemDoubleClicked.connect(self.delete_pole)

    def format_complex(self, c):
        """Format complex number for display"""
        if c.imag == 0:
            return f"{c.real:.3f}"
        elif c.real == 0:
            return f"{c.imag:.3f}j"
        else:
            sign = '+' if c.imag >= 0 else ''
            return f"{c.real:.3f}{sign}{c.imag:.3f}j"

    def parse_complex(self, text):
        """Parse complex number from string"""
        try:
            if 'j' in text:
                return complex(text.replace(' ', ''))
            else:
                return complex(float(text), 0)
        except ValueError:
            return None

    def update_from_filter(self, filter_instance):
        """Update the widget display from filter data"""
        self.zeros_list.clear()
        self.poles_list.clear()

        for zero in filter_instance.zeros:
            self.zeros_list.addItem(self.format_complex(zero))

        for pole in filter_instance.poles:
            self.poles_list.addItem(self.format_complex(pole))

    def notify_filter_change(self):
        """Update the filter with current widget data"""
        zeros = [self.parse_complex(self.zeros_list.item(i).text())
                 for i in range(self.zeros_list.count())]
        poles = [self.parse_complex(self.poles_list.item(i).text())
                 for i in range(self.poles_list.count())]

        # Remove any None values that resulted from parsing errors
        zeros = [z for z in zeros if z is not None]
        poles = [p for p in poles if p is not None]

        self.filter.update_from_element_list(zeros, poles, self)

    def clear_zeros(self):
        self.zeros_list.clear()
        self.notify_filter_change()

    def clear_poles(self):
        self.poles_list.clear()
        self.notify_filter_change()

    def clear_all(self):
        self.clear_zeros()
        self.clear_poles()

    def swap_all(self):
        """Swap all zeros and poles"""
        # Get all items from both lists
        zeros = [self.parse_complex(self.zeros_list.item(i).text())
                 for i in range(self.zeros_list.count())]
        poles = [self.parse_complex(self.poles_list.item(i).text())
                 for i in range(self.poles_list.count())]

        # Clear both lists
        self.zeros_list.clear()
        self.poles_list.clear()

        # Swap the contents
        for pole in poles:
            if pole is not None:
                self.zeros_list.addItem(self.format_complex(pole))

        for zero in zeros:
            if zero is not None:
                self.poles_list.addItem(self.format_complex(zero))

        # Update the filter
        self.notify_filter_change()

    def delete_zero(self, item):
        self.zeros_list.takeItem(self.zeros_list.row(item))
        self.notify_filter_change()

    def delete_pole(self, item):
        self.poles_list.takeItem(self.poles_list.row(item))
        self.notify_filter_change()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = ElementsListWidget()
    widget.show()
    sys.exit(app.exec())
