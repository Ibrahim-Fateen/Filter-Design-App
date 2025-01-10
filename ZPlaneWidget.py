import sys
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QCheckBox, QPushButton, QApplication, QToolTip)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor

from logger_config import setup_logger
logger = setup_logger(__name__)


class ZPlaneElement:
    def __init__(self, position, is_phantom=False, parent_index=-1):
        self.position = position
        self.is_phantom = is_phantom
        self.parent_index = parent_index

class ZPlaneWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 500)
        self.setMouseTracking(True)  # Enable mouse tracking for guidelines
        self.zeros = []
        self.poles = []
        self.dragging_item = None
        self.dragging_type = None
        self.dragging_index = -1
        self.add_mode = None
        self.history = []
        self.history_index = -1
        self.conjugate_mode = True
        self.hover_pos = None
        self.dragging_new = False
        self.drag_start_pos = None

        self.setup_ui()
        self.save_state()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Top controls
        top_controls = QHBoxLayout()

        # Zero button with tooltip
        zero_layout = QHBoxLayout()
        zero_symbol = QLabel("⭘")
        zero_symbol.setStyleSheet("font-size: 20px;")
        zero_text = QLabel("Zero")
        zero_layout.addWidget(zero_symbol)
        zero_layout.addWidget(zero_text)
        self.zero_widget = QWidget()
        self.zero_widget.setLayout(zero_layout)
        self.zero_widget.setToolTip("Drag to add zero on plane")
        self.zero_widget.mousePressEvent = self.start_drag_zero
        self.zero_widget.setStyleSheet("QWidget:hover { background-color: #e0e0e0; }")
        self.zero_widget.setCursor(Qt.CursorShape.PointingHandCursor)

        # Pole button with tooltip
        pole_layout = QHBoxLayout()
        pole_symbol = QLabel("×")
        pole_symbol.setStyleSheet("font-size: 20px;")
        pole_text = QLabel("Pole")
        pole_layout.addWidget(pole_symbol)
        pole_layout.addWidget(pole_text)
        self.pole_widget = QWidget()
        self.pole_widget.setLayout(pole_layout)
        self.pole_widget.setToolTip("Drag to add pole on plane")
        self.pole_widget.mousePressEvent = self.start_drag_pole
        self.pole_widget.setStyleSheet("QWidget:hover { background-color: #e0e0e0; }")
        self.pole_widget.setCursor(Qt.CursorShape.PointingHandCursor)

        self.conjugate_checkbox = QCheckBox("Show Conjugates")
        self.conjugate_checkbox.setChecked(True)
        self.conjugate_checkbox.clicked.connect(self.toggle_conjugate_mode)
        # self.conjugate_checkbox.stateChanged.connect(self.toggle_conjugate_mode) # fixed the state being overwritten when toggling

        self.undo_button = QPushButton("↩ Undo")
        self.redo_button = QPushButton("↪ Redo")
        self.undo_button.clicked.connect(self.undo)
        self.redo_button.clicked.connect(self.redo)

        top_controls.addWidget(self.zero_widget)
        top_controls.addWidget(self.pole_widget)
        top_controls.addWidget(self.conjugate_checkbox)
        top_controls.addWidget(self.undo_button)
        top_controls.addWidget(self.redo_button)
        top_controls.addStretch()

        self.pos_label = QLabel("Position: ")
        self.pos_label.setAlignment(Qt.AlignLeft)

        layout.addLayout(top_controls)
        layout.addStretch()
        layout.addWidget(self.pos_label)

    def start_drag_zero(self, event):
        self.dragging_new = True
        self.add_mode = 'zero'
        self.drag_start_pos = event.pos()

    def start_drag_pole(self, event):
        self.dragging_new = True
        self.add_mode = 'pole'
        self.drag_start_pos = event.pos()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) * 0.4

        # Draw guidelines
        self.draw_guidelines(painter, center, radius)

        # Draw unit circle and main axes with higher contrast
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawEllipse(center, radius, radius)
        painter.drawLine(int(center.x() - radius * 2), int(center.y()),
                         int(center.x() + radius * 2), int(center.y()))
        painter.drawLine(int(center.x()), int(center.y() - radius * 2),
                         int(center.x()), int(center.y() + radius * 2))

        # Draw existing elements
        self.draw_elements(painter, self.zeros, is_pole=False)
        self.draw_elements(painter, self.poles, is_pole=True)

        # Draw dragging preview
        if self.dragging_new and self.hover_pos:
            pos = self.point_to_complex(self.hover_pos)
            if self.add_mode == 'zero':
                self.draw_zero(painter, self.hover_pos, phantom=False)
                # if self.conjugate_mode:
                #     conj_point = self.complex_to_point(pos.conjugate())
                #     self.draw_zero(painter, conj_point, phantom=True)
                conj_point = self.complex_to_point(pos.conjugate())
                self.draw_zero(painter, conj_point, phantom=True)
            else:
                self.draw_pole(painter, self.hover_pos, phantom=False)
                # if self.conjugate_mode:
                #     conj_point = self.complex_to_point(pos.conjugate())
                #     self.draw_pole(painter, conj_point, phantom=True)
                conj_point = self.complex_to_point(pos.conjugate())
                self.draw_pole(painter, conj_point, phantom=True)

    def draw_guidelines(self, painter, center, radius):
        # Draw radius circles
        for r in np.arange(0.2, 2.1, 0.2):
            color = QColor(200, 200, 200) if abs(r - 1.0) > 0.01 else QColor(100, 100, 100)
            if self.hover_pos:
                hover_r = np.sqrt(
                    ((self.hover_pos.x() - center.x()) / radius) ** 2 +
                    ((self.hover_pos.y() - center.y()) / radius) ** 2
                )
                if abs(hover_r - r) < 0.1:
                    color = QColor(100, 100, 200)
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(center, r * radius, r * radius)

            # Draw radius value
            if abs(r - int(r)) < 0.01:  # Only label whole numbers
                painter.drawText(
                    center.x() + r * radius + 5,
                    center.y() - 5,
                    f"{r:.1f}"
                )

        # Draw angle lines
        for angle in range(0, 360, 15):
            rad = np.radians(angle)
            color = QColor(200, 200, 200)
            if self.hover_pos:
                hover_angle = np.degrees(np.arctan2(
                    -(self.hover_pos.y() - center.y()),
                    self.hover_pos.x() - center.x()
                ))
                hover_angle = (hover_angle + 360) % 360
                if abs(hover_angle - angle) < 5:
                    color = QColor(100, 100, 200)

            painter.setPen(QPen(color, 1))
            painter.drawLine(
                center.x(), center.y(),
                center.x() + 2 * radius * np.cos(rad),
                center.y() - 2 * radius * np.sin(rad)
            )

            # Draw angle value
            if angle % 45 == 0:
                text_radius = 1.1 * radius
                painter.drawText(
                    center.x() + text_radius * np.cos(rad) - 15,
                    center.y() - text_radius * np.sin(rad) + 5,
                    f"{self.angle_to_pi_str(angle)}"
                )

    def snap_to_guidelines(self, position):
        """Snap position to guidelines if close enough"""
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) * 0.4

        # Convert to complex for easier calculations
        z = self.point_to_complex(position)

        # Calculate current radius and angle
        r = abs(z)
        theta = np.angle(z)

        # Snap radius to 0.2 increments if close enough
        RADIUS_SNAP_THRESHOLD = 0.05  # Adjustable threshold
        r_normalized = r / 0.2
        r_rounded = round(r_normalized) * 0.2
        if abs(r - r_rounded) < RADIUS_SNAP_THRESHOLD:
            r = r_rounded

        # Snap angle to 15-degree increments if close enough
        ANGLE_SNAP_THRESHOLD = np.radians(2.5)  # 5 degrees threshold
        theta_degrees = np.degrees(theta)
        theta_normalized = theta_degrees / 15
        theta_rounded = round(theta_normalized) * 15
        if abs(np.radians(theta_degrees - theta_rounded)) < ANGLE_SNAP_THRESHOLD:
            theta = np.radians(theta_rounded)

        # Convert back to complex
        z_snapped = r * np.exp(1j * theta)

        # Convert back to point
        return self.complex_to_point(z_snapped)

    def angle_to_pi_str(self, angle):
        """Convert angle in degrees to a string representation in terms of π"""
        rad = angle / 180  # Convert to ratio of π
        if rad == 0:
            return "0"
        elif rad == 1:
            return "π"
        elif rad == 2:
            return "2π"
        elif rad == 0.5:
            return "π/2"
        elif rad == 1.5:
            return "3π/2"
        elif rad == 0.25:
            return "π/4"
        elif rad == 0.75:
            return "3π/4"
        elif rad == 1.25:
            return "5π/4"
        elif rad == 1.75:
            return "7π/4"
        else:
            return f"{rad:.2f}π"

    def draw_elements(self, painter, elements, is_pole):
        """Draw all visible elements (normal and phantom conjugates if enabled)"""
        for element in elements:
            # Skip phantom elements if conjugate mode is disabled
            # if element.is_phantom and not self.conjugate_mode:
            #     continue

            point = self.complex_to_point(element.position)

            if is_pole:
                self.draw_pole(painter, point, element.is_phantom)
            else:
                self.draw_zero(painter, point, element.is_phantom)

    def draw_zero(self, painter, point, phantom=False):
        painter.setOpacity(0.2 if phantom and not self.conjugate_mode else 1.0)
        painter.setPen(QPen(Qt.blue, 2))
        size = 5
        painter.drawEllipse(point, size, size)

    def draw_pole(self, painter, point, phantom=False):
        painter.setOpacity(0.2 if phantom and not self.conjugate_mode else 1.0)
        painter.setPen(QPen(Qt.red, 2))
        size = 5
        painter.drawLine(point.x() - size, point.y() - size,
                         point.x() + size, point.y() + size)
        painter.drawLine(point.x() - size, point.y() + size,
                         point.x() + size, point.y() - size)

    def mousePressEvent(self, event):
        if self.dragging_new:
            return  # If we're already dragging a new element, don't do anything else

        # Check if clicking on existing elements
        pos = event.pos()
        self.dragging_item = None

        # Check zeros
        for i, element in enumerate(self.zeros):
            if not element.is_phantom or self.conjugate_mode:
                if (self.complex_to_point(element.position) - pos).manhattanLength() < 10:
                    self.dragging_item = element
                    self.dragging_type = 'zero'
                    self.dragging_index = i
                    break

        # Check poles
        if not self.dragging_item:
            for i, element in enumerate(self.poles):
                if not element.is_phantom or self.conjugate_mode:
                    if (self.complex_to_point(element.position) - pos).manhattanLength() < 10:
                        self.dragging_item = element
                        self.dragging_type = 'pole'
                        self.dragging_index = i
                        break

    def mouseMoveEvent(self, event):
        self.hover_pos = event.pos()

        # Get potentially snapped position
        snapped_pos = self.snap_to_guidelines(event.pos())
        z = self.point_to_complex(snapped_pos)
        self.pos_label.setText(f"Position: {z.real:.2f} + {z.imag:.2f}j")

        if self.dragging_new:
            self.hover_pos = snapped_pos
            self.update()
        elif self.dragging_item:
            elements = self.zeros if self.dragging_type == 'zero' else self.poles
            new_pos = self.point_to_complex(snapped_pos)

            if self.dragging_item.is_phantom:
                parent = elements[self.dragging_item.parent_index]
                parent.position = new_pos.conjugate()
                self.dragging_item.position = new_pos
            else:
                self.dragging_item.position = new_pos
                # if self.conjugate_mode:
                    # for element in elements:
                    #     if element.is_phantom and element.parent_index == self.dragging_index:
                    #         element.position = new_pos.conjugate()
                for element in elements:
                    if element.is_phantom and element.parent_index == self.dragging_index:
                        element.position = new_pos.conjugate()
                        break

            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging_new:
            snapped_pos = self.snap_to_guidelines(event.pos())
            z = self.point_to_complex(snapped_pos)
            self.add_element(z, self.add_mode)
            self.dragging_new = False
            self.add_mode = None
            self.drag_start_pos = None
            self.save_state()
        elif self.dragging_item:
            snapped_pos = self.snap_to_guidelines(event.pos())
            new_pos = self.point_to_complex(snapped_pos)

            if self.dragging_item.is_phantom:
                elements = self.zeros if self.dragging_type == 'zero' else self.poles
                parent = elements[self.dragging_item.parent_index]
                parent.position = new_pos.conjugate()
                self.dragging_item.position = new_pos
            else:
                self.dragging_item.position = new_pos

            self.dragging_item = None
            self.dragging_type = None
            self.dragging_index = -1
            self.save_state()

        self.hover_pos = None
        self.update()

    def toggle_conjugate_mode(self, state):
        self.conjugate_mode = self.conjugate_checkbox.isChecked()
        self.update()
        self.save_state()

    def add_element(self, position, element_type):
        """Add a new element and its phantom conjugate if needed"""
        new_element = ZPlaneElement(position)
        elements = self.zeros if element_type == 'zero' else self.poles

        # Add the main element
        elements.append(new_element)
        main_index = len(elements) - 1

        phantom = ZPlaneElement(position.conjugate(), is_phantom=True, parent_index=main_index)
        elements.append(phantom)

    def complex_to_point(self, z):
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) * 0.4
        x = center.x() + z.real * radius
        y = center.y() - z.imag * radius
        return QPointF(x, y)

    def point_to_complex(self, point):
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) * 0.4
        x = (point.x() - center.x()) / radius
        y = -(point.y() - center.y()) / radius
        return complex(x, y)

    def start_add_mode(self, mode):
        self.add_mode = mode

    def save_state(self):
        self.history = self.history[:self.history_index + 1]
        state = {
            'zeros': [ZPlaneElement(e.position, e.is_phantom, e.parent_index)
                      for e in self.zeros],
            'poles': [ZPlaneElement(e.position, e.is_phantom, e.parent_index)
                      for e in self.poles],
            'conjugate_enabled': self.conjugate_mode
        }
        self.history.append(state)
        self.history_index += 1
        self.update_undo_redo_state()

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.zeros = [ZPlaneElement(e.position, e.is_phantom, e.parent_index)
                          for e in state['zeros']]
            self.poles = [ZPlaneElement(e.position, e.is_phantom, e.parent_index)
                          for e in state['poles']]
            self.conjugate_mode = state['conjugate_enabled']
            self.conjugate_checkbox.setChecked(self.conjugate_mode)
            self.update_undo_redo_state()
            self.update()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.zeros = [ZPlaneElement(e.position, e.is_phantom, e.parent_index)
                          for e in state['zeros']]
            self.poles = [ZPlaneElement(e.position, e.is_phantom, e.parent_index)
                          for e in state['poles']]
            self.conjugate_mode = state['conjugate_enabled']
            self.conjugate_checkbox.setChecked(self.conjugate_mode)
            self.update_undo_redo_state()
            self.update()

    def update_undo_redo_state(self):
        self.undo_button.setEnabled(self.history_index > 0)
        self.redo_button.setEnabled(self.history_index < len(self.history) - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ZPlaneWidget()
    widget.show()
    sys.exit(app.exec())
