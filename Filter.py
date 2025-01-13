import numpy as np
from scipy import signal
import json
from pathlib import Path


class Filter:
    def __init__(self):
        self.zeros = []  # List of complex numbers
        self.poles = []  # List of complex numbers
        self.gain = 1.0

        # Create filters directory if it doesn't exist
        self.filters_dir = Path(__file__).parent / 'filters'
        self.filters_dir.mkdir(exist_ok=True)

        self.subscribers = []  # Subscribers should include callback functions for: Magnitude plot, Phase plot, and elements list.

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def notify_subscribers(self):
        for callback in self.subscribers:
            callback(self)

    def update_from_zplane(self, zeros, poles):
        """Update filter coefficients from z-plane widget"""
        self.zeros = [complex(z.position.real, z.position.imag) for z in zeros]
        self.poles = [complex(p.position.real, p.position.imag) for p in poles]
        self.notify_subscribers()
        # self.zeros = [complex(z.position.real, z.position.imag)
        #               for z in zeros if not z.is_phantom]
        # self.poles = [complex(p.position.real, p.position.imag)
        #               for p in poles if not p.is_phantom]
        # self._normalize_gain()

    def _normalize_gain(self):
        """Normalize filter gain to 1 at DC (z = 1)"""
        if not self.zeros and not self.poles:
            self.gain = 1.0
            return

        # Calculate gain at z = 1 (DC)
        num = np.prod([1 - z for z in self.zeros]) if self.zeros else 1
        den = np.prod([1 - p for p in self.poles]) if self.poles else 1

        # Set gain to normalize DC response to 1
        self.gain = abs(den / num) if den != 0 else 1.0

    def get_transfer_function(self):
        """Get filter coefficients in transfer function form"""
        # Convert zeros and poles to polynomials
        b = np.poly(self.zeros) * self.gain if self.zeros else [self.gain]
        a = np.poly(self.poles) if self.poles else [1.0]
        return b, a

    def get_frequency_response(self, num_points=1024):
        """Calculate frequency response"""
        w, h = signal.freqz(*self.get_transfer_function(), worN=num_points)

        # frequencies = w * self.sample_rate / (2 * np.pi)
        magnitude_db = 20 * np.log10(np.abs(h))
        phase_deg = np.angle(h, deg=True)

        return w, magnitude_db, phase_deg

    def get_impulse_response(self, num_points=100):
        """Calculate impulse response"""
        b, a = self.get_transfer_function()
        return signal.lfilter(b, a, [1.0] + [0.0] * (num_points - 1))

    def save_to_file(self, filename):
        """Save filter to JSON file"""
        data = {
            'zeros': [(z.real, z.imag) for z in self.zeros],
            'poles': [(p.real, p.imag) for p in self.poles],
            'gain': self.gain
        }

        filepath = self.filters_dir / f"{filename}.dsp"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename):
        """Load filter from JSON file"""
        filepath = self.filters_dir / f"{filename}.dsp"
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.zeros = [complex(z[0], z[1]) for z in data['zeros']]
        self.poles = [complex(p[0], p[1]) for p in data['poles']]
        self.gain = data['gain']
        self.notify_subscribers()
