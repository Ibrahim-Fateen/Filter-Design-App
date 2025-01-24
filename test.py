from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

from Filter import Filter
from PlotsWidget import FilterPlotsWidget
from ZPlaneWidget import ZPlaneWidget
from ElementsListWidget import ElementsListWidget
from FilterRealizer import FilterRealizer


class FilterRealizerWidget(QWidget):
    def __init__(self, filter):
        super().__init__()
        self.filter_realizer = FilterRealizer(filter)

        self.cascade_button = QPushButton("Show Cascade Form")
        self.direct_form_ii_button = QPushButton("Show Direct Form II")

        self.cascade_button.clicked.connect(self.show_cascade)
        self.direct_form_ii_button.clicked.connect(self.show_direct_form_ii)

        layout = QVBoxLayout()
        layout.addWidget(self.cascade_button)
        layout.addWidget(self.direct_form_ii_button)
        self.setLayout(layout)

    def show_cascade(self):
        self.filter_realizer.draw_cascade_form()
        self.filter_realizer.show()

    def show_direct_form_ii(self):
        self.filter_realizer.draw_direct_form_2()
        self.filter_realizer.show()


if __name__ == '__main__':
    app = QApplication()

    # Create filter and widgets
    filter = Filter()
    zplane = ZPlaneWidget()
    plots = FilterPlotsWidget()
    elements_list = ElementsListWidget()
    realizer_widget = FilterRealizerWidget(filter)

    zplane.set_filter(filter)
    plots.set_filter(filter)
    elements_list.set_filter(filter)

    # Show widgets
    zplane.show()
    plots.show()
    elements_list.show()
    realizer_widget.show()

    app.exec()
