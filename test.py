from PySide6.QtWidgets import QApplication

from Filter import Filter
from PlotsWidget import FilterPlotsWidget
from ZPlaneWidget import ZPlaneWidget
from ElementsListWidget import ElementsListWidget

if __name__ == '__main__':
    app = QApplication()

    # Create filter and widgets
    filter = Filter()
    zplane = ZPlaneWidget()
    plots = FilterPlotsWidget()
    elements_list = ElementsListWidget()

    zplane.set_filter(filter)
    plots.set_filter(filter)
    elements_list.set_filter(filter)

    # Show widgets
    zplane.show()
    plots.show()
    elements_list.show()

    app.exec()
