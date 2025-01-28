import numpy as np
from numpy.typing import NDArray
from scipy import signal
class DigitalSignal:
    def __init__(self, data, sampling_rate = 100):
        self.data = np.array(data)
        self.sampling_rate = sampling_rate
        self.time = np.arange(len(data)) / sampling_rate

    def apply_filter(self, filter_obj):
        """
        Apply a filter to the signal.
        """

        Numerator, Denominator = filter_obj.get_transfer_function()
        
        filtered_data = signal.lfilter(Numerator, Denominator, self.data)

        filtered_data = np.real(filtered_data)
            
        return DigitalSignal(filtered_data, self.sampling_rate)
    
    @classmethod
    def convert_to_numpy(cls, csv_file_path, skip_header=1):
        """
        Convert a csv file to a numpy array and return a DigitalSignal instance.
        """
        data = np.genfromtxt(csv_file_path, delimiter=',', skip_header=skip_header)
        return cls(data, sampling_rate=1000)  # Default 1kHz sampling rate


# t = np.linspace(0, 1, 1000)
# data = np.sin(2 * np.pi * 5 * t) + 0.5 * np.sin(2 * np.pi * 100 * t)
# sampling_rate = 1000
# signal_obj = Signal(data, sampling_rate)

# # Create and configure a low-pass filter
# filter_obj = Filter()
# filter_obj.add_pole(0.95)  # Pole very close to unit circle for stronger low-pass effect
# filter_obj.add_zero(0)  # Zero at origin for better low-pass characteristics
# filter_obj.gain = 0.05  # Adjust gain to maintain reasonable amplitude

# # Apply filter and plot results
# filtered_signal = signal_obj.apply_filter(filter_obj)

# # Plot original and filtered signals
# signal_obj.plot()
# filtered_signal.plot()
