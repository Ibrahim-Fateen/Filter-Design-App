import numpy as np
import pandas as pd

# Parameters
fs = 100  # Sampling frequency (Hz)
t = np.linspace(0, 100, 10000)  # Time array with 10000 points
f1 = 5  # First frequency (Hz)
f2 = 10  # Second frequency (Hz)

# Generate the composite signal
signal = np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(2 * np.pi * f2 * t)

# Create DataFrame
df = pd.DataFrame({
    'Signal': signal
})

# Save to CSV
df.to_csv('test_signal.csv', index=False)