from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np
from Signal import DigitalSignal
from Filter import Filter

class FilterUsageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.initializeVariables()
        self.connectSignals()

    def setupUi(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.controlPanel = QtWidgets.QHBoxLayout()
        
        self.modeCheckbox = QtWidgets.QCheckBox("Real-time Mode")
        self.browseButton = QtWidgets.QPushButton("Browse Signal")
        
        self.speedLabel = QtWidgets.QLabel("Speed:")
        self.speedSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speedSlider.setRange(1, 100)
        self.speedSlider.setValue(10)
        
        self.playButton = QtWidgets.QPushButton("Play/Pause")
        
        self.controlPanel.addWidget(self.modeCheckbox)
        self.controlPanel.addWidget(self.browseButton)
        self.controlPanel.addWidget(self.speedLabel)
        self.controlPanel.addWidget(self.speedSlider)
        self.controlPanel.addWidget(self.playButton)
        
        self.inputPlot = pg.PlotWidget(title="Input Signal")
        self.filteredPlot = pg.PlotWidget(title="Filtered Signal")
        
        self.filteredPlot.setXLink(self.inputPlot)
        
        self.mousePad = QtWidgets.QFrame()
        self.mousePad.setMinimumSize(200, 100)
        self.mousePad.setFrameStyle(QtWidgets.QFrame.Box)
        self.mousePad.setVisible(False)
        
        self.layout.addLayout(self.controlPanel)
        self.layout.addWidget(self.mousePad)
        self.layout.addWidget(self.inputPlot)
        self.layout.addWidget(self.filteredPlot)
        
        self.inputPlot.setLimits(xMin=0, yMin=-1000, yMax=1000)  
        self.filteredPlot.setLimits(xMin=0, yMin=-1000, yMax=1000)
        
        self.inputPlot.enableAutoRange()
        self.filteredPlot.enableAutoRange()

    def initializeVariables(self):
        self.playing = False
        self.real_time_mode = False
        self.speed = 10
        self.buffer_size = 1000
        self.signal_buffer = np.zeros(self.buffer_size)
        self.filtered_buffer = np.zeros(self.buffer_size)
        
        # Modified time array initialization
        self.base_sampling_rate = 1000  # Base rate in Hz
        self.updateTimeArray()
        
        self.view_percentage = 0.02  
        self.current_position = 0
        self.zoom_level = 1.0
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateView)

    def updateTimeArray(self):
        # Calculate temporal resolution based on slider
        self.temporal_resolution = self.speed / 10.0  # seconds per point
        self.time_array = np.arange(self.buffer_size) * self.temporal_resolution

    def connectSignals(self):
        self.modeCheckbox.toggled.connect(self.toggleMode)
        self.browseButton.clicked.connect(self.browseFile)
        self.playButton.clicked.connect(self.togglePlay)
        self.speedSlider.valueChanged.connect(self.updateSpeed)
        self.mousePad.mouseMoveEvent = self.mouseMoveEvent

    def toggleMode(self, checked):
        self.real_time_mode = checked
        self.mousePad.setVisible(checked)
        self.browseButton.setEnabled(not checked)
        if checked:
            self.signal_buffer = np.zeros(self.buffer_size)
            self.filtered_buffer = np.zeros(self.buffer_size)
            self.timer.timeout.disconnect()  
            self.timer.timeout.connect(self.updateRealTime)
        else:
            self.timer.timeout.disconnect()
            self.timer.timeout.connect(self.updateView)
        

    def browseFile(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Signal", "", "CSV files (*.csv)")
        if filename:
            self.signal = DigitalSignal.convert_to_numpy(filename)
            self.updatePlots()

    def updateSpeed(self, value):
        self.speed = value
        if self.playing:
            if self.real_time_mode:
                # Update temporal resolution
                self.updateTimeArray()
                # Update timer interval based on temporal resolution
                interval = int(self.temporal_resolution * 1000)  # Convert to milliseconds
                self.timer.setInterval(max(10, interval))
            else:
                # File mode speed control remains the same
                interval = max(10, int(1000/value))
                self.timer.setInterval(interval)

    def togglePlay(self):
        self.playing = not self.playing
        if self.playing:
            self.timer.start(50)
            self.playButton.setText("Pause")
        else:
            self.timer.stop() 
            self.playButton.setText("Play")

    def mouseMoveEvent(self, event):
        if self.real_time_mode and self.playing:
            self.signal_buffer = np.roll(self.signal_buffer, -1)
            self.signal_buffer[-1] = event.x()
            
            self.updateRealTime()

    def updateView(self):
        if not self.real_time_mode and self.playing and hasattr(self, 'signal'):
            signal_length = len(self.signal.data)
            window_size = int(signal_length * self.view_percentage * self.zoom_level)
            
            self.current_position += self.speed
            
            if self.current_position >= signal_length:
                self.current_position = 0
                
            start = max(0, self.current_position)
            end = min(signal_length, start + window_size)
            
            self.inputPlot.setXRange(start/self.signal.sampling_rate, 
                                    end/self.signal.sampling_rate)
            self.filteredPlot.setXRange(start/self.signal.sampling_rate, 
                                    end/self.signal.sampling_rate)
            
            self.updatePlots()

    def updateRealTime(self):
        if self.real_time_mode and self.playing:
            self.inputPlot.clear()
            self.filteredPlot.clear()
            
            # Plot with updated time array
            self.inputPlot.plot(self.time_array, self.signal_buffer)
            
            if hasattr(self, 'filter'):
                real_time_signal = DigitalSignal(self.signal_buffer, 
                                               int(1/self.temporal_resolution))
                filtered_data = real_time_signal.apply_filter(self.filter).data
                self.filteredPlot.plot(self.time_array, filtered_data)
            
            # Update x-axis range to show full buffer
            total_time = self.buffer_size * self.temporal_resolution
            self.inputPlot.setXRange(0, total_time)
            self.filteredPlot.setXRange(0, total_time)

    def wheelEvent(self, event):
        if not self.real_time_mode:
            if event.angleDelta().y() > 0:
                self.zoom_level = max(0.1, self.zoom_level - 0.1)
            else:
                self.zoom_level = min(1.0, self.zoom_level + 0.1)
            self.updateView()

    def updatePlots(self):
        if self.real_time_mode:
            self.inputPlot.clear()
            self.filteredPlot.clear()
            self.inputPlot.plot(self.time_array, self.signal_buffer)
            if hasattr(self, 'filter'):
                filtered_signal = DigitalSignal(self.signal_buffer, 1000)
                self.filtered_buffer = filtered_signal.apply_filter(self.filter).data
                self.filteredPlot.plot(self.time_array, self.filtered_buffer)
        else:
            if hasattr(self, 'signal'):
                self.inputPlot.clear()
                self.filteredPlot.clear()
                self.inputPlot.plot(self.signal.time, self.signal.data)
                if hasattr(self, 'filter'):
                    filtered_signal = self.signal.apply_filter(self.filter)
                    self.filteredPlot.plot(filtered_signal.time, filtered_signal.data)
        
        # self.updatePlotLimits()

    def updatePlotLimits(self):
        xMin = 0
        xMax = 1
        yMin = -1000
        yMax = 1000

        try:
            if self.real_time_mode:
                if hasattr(self, 'signal_buffer') and hasattr(self, 'filtered_buffer'):
                    yMin = min(np.min(self.signal_buffer), np.min(self.filtered_buffer)) * 1.1
                    yMax = max(np.max(self.signal_buffer), np.max(self.filtered_buffer)) * 1.1
            else:
                if hasattr(self, 'signal') and self.signal is not None:
                    xMax = len(self.signal.data) / self.signal.sampling_rate
                    yMin = np.min(self.signal.data) * 1.1
                    yMax = np.max(self.signal.data) * 1.1

            if not all(map(np.isfinite, [xMin, xMax, yMin, yMax])):
                return

            self.inputPlot.setLimits(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)
            self.filteredPlot.setLimits(xMin=xMin, xMax=xMax, yMin=yMin, yMax=yMax)
            
        except (AttributeError, ValueError) as e:
            print(f"Error updating plot limits: {e}")

    def setFilter(self, filter_obj):
        self.filter = filter_obj
        self.updatePlots()

filter_obj = Filter()
filter_obj.add_pole(0.95)
filter_obj.add_zero(0)
filter_obj.gain = 0.05

app = QtWidgets.QApplication([])
window = FilterUsageWidget()
window.setFilter(filter_obj)

window.show()

app.exec_()
