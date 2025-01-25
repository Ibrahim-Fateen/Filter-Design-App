import sys
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QCheckBox, QPushButton, QApplication, QToolTip)
from PySide6.QtCore import Qt, QPointF, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap

from logger_config import setup_logger
logger = setup_logger(__name__)


class ZPlaneElement:
    def __init__(self, position, is_phantom=False):
        self.position = position
        self.is_phantom = is_phantom
        self.conjugate = None  # Reference to conjugate pair

    def create_conjugate(self):
        """Create and link a conjugate pair"""
        if not self.conjugate:
            phantom = ZPlaneElement(self.position.conjugate(), is_phantom=True)
            phantom.conjugate = self
            self.conjugate = phantom
            return phantom
        return None

    def update_position(self, new_pos):
        """Update position of element and its conjugate"""
        self.position = new_pos
        if self.conjugate:
            self.conjugate.position = new_pos.conjugate()


class ZPlaneWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 500)
        self.setMouseTracking(True)
        self.zeros = []
        self.poles = []
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 4.0
        self.dragging_item = None
        self.dragging_type = None
        self.add_mode = None
        self.history = []
        self.history_index = -1
        self.conjugate_mode = True
        self.hover_pos = None
        self.dragging_new = False
        self.drag_start_pos = None
        self.trash_rect = QRect()
        self.trash_open = False
        self.filter = None
        self._updating_from_filter = False

        self.trash_closed_icon = QPixmap("icons/trash-closed.png")
        self.trash_opened_icon = QPixmap("icons/trash-opened.png")

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

        self.conjugate_checkbox = QCheckBox("Auto Add Conjugates")
        self.conjugate_checkbox.setChecked(True)
        self.conjugate_checkbox.clicked.connect(self.toggle_conjugate_mode)

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

    def set_filter(self, filter_instance):
        self.filter = filter_instance
        self.filter.subscribe(self.on_filter_update, self)
        self.zeros = [ZPlaneElement(complex(z.real, z.imag)) for z in filter_instance.zeros]
        self.poles = [ZPlaneElement(complex(p.real, p.imag)) for p in filter_instance.poles]
        self.conjugate_mode = False
        self.conjugate_checkbox.setChecked(False)
        self.save_state()
        self.update()

    def on_filter_update(self, filter_instance):
        self._updating_from_filter = True
        self.zeros = []
        self.poles = []

        # Convert filter zeros/poles to complex numbers if they aren't already
        zero_positions = [complex(z.real, z.imag) for z in filter_instance.zeros]
        pole_positions = [complex(p.real, p.imag) for p in filter_instance.poles]

        # Add elements with proper conjugate linking
        self.add_elements_from_filter(zero_positions, 'zero')
        self.add_elements_from_filter(pole_positions, 'pole')

        self._updating_from_filter = False
        self.save_state()
        self.update()

    def notify_filter_change(self):
        if self.filter:
            zeros = [z for z in self.zeros]
            poles = [p for p in self.poles]

            self.filter.update_from_zplane(zeros, poles, self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        trash_size = 32  # Size of the trash can icon
        padding = 10  # Padding from widget edges
        self.trash_rect = QRect(
            self.width() - trash_size - padding,
            self.height() - trash_size - padding,
            trash_size,
            trash_size
        )

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
        scaled_radius = radius * self.zoom_level
        painter.drawEllipse(center, scaled_radius, scaled_radius)
        painter.drawLine(int(center.x() - scaled_radius * 15), int(center.y()),
                        int(center.x() + scaled_radius * 15), int(center.y()))
        painter.drawLine(int(center.x()), int(center.y() - scaled_radius * 15),
                        int(center.x()), int(center.y() + scaled_radius * 15))

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

        painter.setOpacity(1)
        if self.trash_open:
            painter.drawPixmap(self.trash_rect, self.trash_opened_icon)
        else:
            painter.drawPixmap(self.trash_rect, self.trash_closed_icon)

    def draw_guidelines(self, painter, center, radius):
        # Draw radius circles
        for r in np.arange(0.2, 10.2, 0.2):  # Extended to 10
            if r > 2.0 and r % 1 != 0:  # Skip non-integer circles beyond 2
                continue
            
            color = QColor(200, 200, 200) if abs(r - 1.0) > 0.01 else QColor(100, 100, 100)
            if self.hover_pos:
                hover_r = np.sqrt(
                    ((self.hover_pos.x() - center.x()) / (radius * self.zoom_level)) ** 2 +
                    ((self.hover_pos.y() - center.y()) / (radius * self.zoom_level)) ** 2
                )
                if abs(hover_r - r) < 0.1:
                    color = QColor(100, 100, 200)
            
            scaled_radius = r * radius * self.zoom_level
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(center, scaled_radius, scaled_radius)

            # Draw radius value
            if r <= 2.0 or r.is_integer():  # Show all labels up to 2, then only integers
                painter.drawText(
                    center.x() + scaled_radius + 5,
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
        """Draw all elements, showing phantoms only if conjugate mode is enabled"""
        draw_func = self.draw_pole if is_pole else self.draw_zero
        for element in elements:
            position = self.complex_to_point(element.position)
            draw_func(painter, position)

    def draw_zero(self, painter, point, phantom=False):
        painter.setOpacity(0.2 if phantom else 1.0)
        painter.setPen(QPen(Qt.blue, 2))
        size = 5
        painter.drawEllipse(point, size, size)

    def draw_pole(self, painter, point, phantom=False):
        painter.setOpacity(0.2 if phantom else 1.0)
        painter.setPen(QPen(Qt.red, 2))
        size = 5
        painter.drawLine(point.x() - size, point.y() - size,
                         point.x() + size, point.y() + size)
        painter.drawLine(point.x() - size, point.y() + size,
                         point.x() + size, point.y() - size)

    def mousePressEvent(self, event):
        if self.dragging_new:
            return

        pos = event.pos()
        self.dragging_item = None

        # Check zeros and poles
        for elements, type_name in [(self.zeros, 'zero'), (self.poles, 'pole')]:
            for i, element in enumerate(elements):
                element_pos = self.complex_to_point(element.position)
                if (element_pos - pos).manhattanLength() < 10:
                    # If clicking on a phantom, use its main element instead
                    if element.is_phantom:
                        self.dragging_item = element.conjugate
                    else:
                        self.dragging_item = element
                    self.dragging_type = type_name
                    self.dragging_index = i
                    return

    def mouseMoveEvent(self, event):
        self.hover_pos = event.pos()

        # Get potentially snapped position
        snapped_pos = self.snap_to_guidelines(event.pos())
        z = self.point_to_complex(snapped_pos)
        self.pos_label.setText(f"Position: {z.real:.2f} + {z.imag:.2f}j")

        if self.dragging_new:
            self.hover_pos = snapped_pos
            near_trash = self.trash_rect.adjusted(-20, -20, 20, 20).contains(event.pos())
            if near_trash != self.trash_open:
                self.trash_open = near_trash
            self.update()
        elif self.dragging_item:
            new_pos = self.point_to_complex(snapped_pos)

            near_trash = self.trash_rect.adjusted(-20, -20, 20, 20).contains(event.pos())
            if near_trash != self.trash_open:
                self.trash_open = near_trash

            # Always update through the main element
            self.dragging_item.update_position(new_pos)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging_item:
            if self.trash_open:
                self.delete_element(self.dragging_item, self.dragging_type)
                self.dragging_item = None
                self.dragging_type = None
                self.dragging_index = -1
                self.trash_open = False
                self.save_state()
                self.notify_filter_change()
                self.update()
                return

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
        self.trash_open = False
        self.notify_filter_change()
        self.update()

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_factor = 1.1
        if event.angleDelta().y() > 0:
            self.zoom_level = min(self.zoom_level * zoom_factor, self.max_zoom)
        else:
            self.zoom_level = max(self.zoom_level / zoom_factor, self.min_zoom)
        self.update()

    def delete_element(self, element, element_type):
        """Delete both an element and its conjugate pair"""
        if element_type == 'zero':
            elements = self.zeros
        else:
            elements = self.poles

        # Remove both the element and its conjugate
        if element.is_phantom:
            elements.remove(element.conjugate)  # Remove the main element
            elements.remove(element)  # Remove the phantom
        else:
            if element.conjugate:
                elements.remove(element.conjugate)  # Remove the phantom
            elements.remove(element)  # Remove the main element

    def toggle_conjugate_mode(self, state):
        self.conjugate_mode = self.conjugate_checkbox.isChecked()
        self.update()
        self.save_state()
        self.notify_filter_change()
        return

    def add_element(self, position, element_type):
        """Add a new element with its conjugate pair"""
        new_element = ZPlaneElement(position)
        elements = self.zeros if element_type == 'zero' else self.poles

        # Add the main element
        elements.append(new_element)

        # Create and add its conjugate
        if not self._updating_from_filter and self.conjugate_mode:
            phantom = new_element.create_conjugate()
            if phantom:
                elements.append(phantom)

    def find_conjugate_pair(self, elements, position):
        """Find an existing element that could be a conjugate pair"""
        for element in elements:
            if abs(element.position.conjugate() - position) < 1e-10:  # Use small epsilon for float comparison
                return element
        return None

    def add_elements_from_filter(self, positions, element_type):
        """Add multiple elements from filter, linking conjugates"""
        elements = self.zeros if element_type == 'zero' else self.poles
        processed = set()  # Keep track of processed positions

        for pos in positions:
            if pos in processed:
                continue

            new_element = ZPlaneElement(pos)
            elements.append(new_element)
            processed.add(pos)

            # Look for conjugate pair in remaining positions
            conj_pos = pos.conjugate()
            if abs(conj_pos.imag) > 1e-10:  # Only look for conjugates if not on real axis
                if conj_pos in positions:
                    phantom = new_element.create_conjugate()
                    if phantom:
                        elements.append(phantom)
                        processed.add(conj_pos)

    def complex_to_point(self, z):
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) * 0.4
        x = center.x() + z.real * radius * self.zoom_level
        y = center.y() - z.imag * radius * self.zoom_level
        return QPointF(x, y)

    def point_to_complex(self, point):
        center = QPointF(self.width() / 2, self.height() / 2)
        radius = min(self.width(), self.height()) * 0.4
        x = (point.x() - center.x()) / (radius * self.zoom_level)
        y = -(point.y() - center.y()) / (radius * self.zoom_level)
        return complex(x, y)

    def start_add_mode(self, mode):
        self.add_mode = mode

    def save_state(self):
        """Save the current state for undo/redo"""
        self.history = self.history[:self.history_index + 1]

        # Create new elements without maintaining references
        state = {
            'zeros': [],
            'poles': [],
            'conjugate_enabled': self.conjugate_mode
        }

        # Save main elements and recreate conjugate relationships
        for elements, key in [(self.zeros, 'zeros'), (self.poles, 'poles')]:
            for element in elements:
                if not element.is_phantom:
                    new_element = ZPlaneElement(element.position)
                    state[key].append(new_element)
                    if element.conjugate:
                        phantom = new_element.create_conjugate()
                        if phantom:
                            state[key].append(phantom)

        self.history.append(state)
        self.history_index += 1
        self.update_undo_redo_state()

    def set_state(self, state):
        self.zeros = [ZPlaneElement(e.position, e.is_phantom) for e in state['zeros']]
        self.poles = [ZPlaneElement(e.position, e.is_phantom) for e in state['poles']]
        self.conjugate_mode = state['conjugate_enabled']
        self.conjugate_checkbox.setChecked(self.conjugate_mode)
        self.update_undo_redo_state()
        self.update()
        self.notify_filter_change()

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.set_state(state)

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.set_state(state)

    def update_undo_redo_state(self):
        self.undo_button.setEnabled(self.history_index > 0)
        self.redo_button.setEnabled(self.history_index < len(self.history) - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ZPlaneWidget()
    widget.show()
    sys.exit(app.exec())
