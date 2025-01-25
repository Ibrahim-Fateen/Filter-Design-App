import sys
import numpy as np
from math import gcd
from PySide6.QtWidgets import QWidget, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, FuncFormatter

from logger_config import setup_logger

logger = setup_logger(__name__)


class FilterPlotsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 400)
        self.setup_ui()
        self.w = None
        self.magnitude_db = None
        self.phase = None

    def setup_ui(self):
        # Create main layout
        layout = QHBoxLayout(self)

        # Create figure with two subplots
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Create magnitude subplot
        self.mag_ax = self.figure.add_subplot(121)
        self.mag_ax.set_title('Magnitude Response')
        self.mag_ax.set_xlabel('ω (rad/sample)')
        self.mag_ax.set_ylabel('Magnitude (dB)')
        self.mag_ax.grid(True)

        # Create phase subplot
        self.phase_ax = self.figure.add_subplot(122)
        self.phase_ax.set_title('Phase Response')
        self.phase_ax.set_xlabel('ω (rad/sample)')
        self.phase_ax.set_ylabel('Phase (rad)')
        self.phase_ax.grid(True)

        # Adjust layout to prevent overlapping
        self.figure.tight_layout()

        # Initialize plot lines
        self.mag_line = None
        self.phase_line = None

        # Store vertical lines for cursor interaction
        self.mag_vline = None
        self.phase_vline = None

        # Connect mouse events
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # Initialize filter reference
        self.filter = None

    def set_filter(self, filter_instance):
        """Connect to a filter instance"""
        filter_instance.subscribe(self.update_plots, self)

    def format_pi_ticks(self, x, pos):
        """Format tick labels in terms of multiples of π/4, with simplifications."""
        multiple = 4  # Denominator for π multiples
        x_pi = x / np.pi
        rounded_x_pi = round(x_pi * multiple) / multiple  # Round to nearest multiple of π/4

        if rounded_x_pi == 0:
            return "0"
        elif rounded_x_pi == 1:
            return "π"
        elif rounded_x_pi == -1:
            return "-π"
        elif rounded_x_pi.is_integer():
            return f"{int(rounded_x_pi)}π"
        else:
            # Simplify the fraction
            numerator = int(rounded_x_pi * multiple)
            denominator = multiple
            divisor = gcd(abs(numerator), denominator)  # Compute GCD for simplification
            numerator //= divisor
            denominator //= divisor

            if denominator == 1:  # Case where the fraction simplifies to a whole number
                return f"{numerator}π"
            elif numerator == 1:  # Avoid "1π/denominator"
                return f"π/{denominator}"
            elif numerator == -1:  # Avoid "-1π/denominator"
                return f"-π/{denominator}"
            else:
                return f"{numerator}π/{denominator}"

    def update_plots(self, filter_instance=None):
        """Update both plots with new filter response"""

        # Get frequency response
        self.w, self.magnitude_db, self.phase = filter_instance.get_frequency_response()

        self.mag_ax.clear()
        self.mag_ax.plot(self.w, self.magnitude_db)
        self.mag_ax.grid(True)
        self.mag_ax.set_title('Magnitude Response')
        self.mag_ax.set_xlabel('ω (rad/sample)')
        self.mag_ax.set_ylabel('Magnitude (dB)')

        # Set reasonable y-axis limits for magnitude
        min_mag = max(min(self.magnitude_db), -100)  # Limit to -100 dB
        max_mag = min(max(self.magnitude_db), 100)  # Limit to 100 dB
        self.mag_ax.set_ylim(min_mag - 10, max_mag + 10)

        # # Add horizontal line at -3dB for reference
        # self.mag_ax.axhline(y=-3, color='r', linestyle='--', alpha=0.5)
        # self.mag_ax.text(self.w[1], -3, '-3 dB', verticalalignment='bottom')

        self.phase_ax.clear()
        self.phase_ax.plot(self.w, self.phase)
        self.phase_ax.grid(True)
        self.phase_ax.set_title('Phase Response')
        self.phase_ax.set_xlabel('ω (rad/sample)')
        self.phase_ax.set_ylabel('Phase (rad)')

        # Set reasonable y-axis limits for phase
        self.phase_ax.set_ylim(-np.pi, np.pi)

        # Add horizontal lines at ±π for reference
        self.phase_ax.axhline(y=np.pi, color='r', linestyle='--', alpha=0.5)
        self.phase_ax.axhline(y=-np.pi, color='r', linestyle='--', alpha=0.5)

        # Set x-axis limits for both plots
        self.mag_ax.set_xlim(0, np.pi)
        self.phase_ax.set_xlim(0, np.pi)

        # Set ticks for both plots
        for ax in [self.mag_ax, self.phase_ax]:
            # Set major ticks at multiples of π/4
            ax.xaxis.set_major_locator(MultipleLocator(np.pi / 4))
            ax.xaxis.set_major_formatter(FuncFormatter(self.format_pi_ticks))

        # Set phase y-axis ticks at multiples of π/4
        self.phase_ax.yaxis.set_major_locator(MultipleLocator(np.pi / 4))
        self.phase_ax.yaxis.set_major_formatter(FuncFormatter(self.format_pi_ticks))

        # Rotate x-axis labels for better readability
        for ax in [self.mag_ax, self.phase_ax]:
            ax.tick_params(axis='x', rotation=45)

        # Update canvas
        self.figure.tight_layout()
        self.canvas.draw()

    def on_mouse_move(self, event):
        """Handle mouse movement to show frequency response at cursor"""
        if event.inaxes in [self.mag_ax, self.phase_ax]:
            # Remove old vertical lines
            if self.mag_vline:
                self.mag_vline.remove()
            if self.phase_vline:
                self.phase_vline.remove()

            # Add new vertical lines at cursor x-position
            self.mag_vline = self.mag_ax.axvline(x=event.xdata, color='k', linestyle=':', alpha=0.5)
            self.phase_vline = self.phase_ax.axvline(x=event.xdata, color='k', linestyle=':', alpha=0.5)

            # Get nearest frequency response values
            if self.w is not None:
                idx = np.abs(self.w - event.xdata).argmin()

                # Update titles with current values
                w_str = f'{event.xdata / np.pi:.2f}π'
                logger.debug(f'w_str: {w_str}')
                logger.debug(f'idx: {idx}')
                logger.debug(f'mag: {self.magnitude_db[idx]}')
                logger.debug(f'phase: {self.phase[idx]}')
                self.mag_ax.set_title(f'Magnitude Response\nω = {w_str}: {self.magnitude_db[idx]:.1f} dB')
                self.phase_ax.set_title(f'Phase Response\nω = {w_str}: {self.phase[idx]:.2f} rad')

            self.canvas.draw()

    def resizeEvent(self, event):
        """Handle widget resize"""
        super().resizeEvent(event)
        self.figure.tight_layout()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from Filter import Filter

    app = QApplication(sys.argv)

    # Create test filter
    filter = Filter()
    filter.zeros = [1]

    # Create and show plots widget
    plots = FilterPlotsWidget()
    plots.set_filter(filter)
    plots.update_plots(filter)
    plots.show()

    sys.exit(app.exec())
