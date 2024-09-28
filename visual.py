import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from PyQt5.QtCore import QThread, pyqtSignal
import paho.mqtt.client as mqtt
import json
from collections import deque
import time

start_time = None

class InsoleModel:
    def __init__(self):
        """
        Initialize the insole layout and sensor positions.\n
        Insole layout is label as following number.\n
        0: No sensor area, 1: Surrounding area, 2: Sensor placement area\n
        Manually collect sensor positions from only one point from each group. Total 16 groups.
        """
        self.my_right_foot = np.array([
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0 ,0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 0, 0, 0, 0],
            [0, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 0, 0, 0],
            [0, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 1, 0],
            [1, 1, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0],
            [1, 1, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0],
            [1, 1, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0],
            [1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 0],
            [1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1],
            [1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1],
            [1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1],
            [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1],
            [0, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1],
            [0, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1],
            [0, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 0],
            [0, 0, 1, 1, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 0],
            [0, 0, 0, 1, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 0],
            [0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 0],
            [0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 0],
            [0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 1, 0],
            [0, 0, 0, 1, 1, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 0, 0],
            [0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 0, 0],
            [0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 0, 0],
            [0, 0, 0, 0, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 2, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        ])
        self.sensor_positions = [
            (6, 4), (5, 11), (15, 4), (15, 9), 
            (15, 15), (24, 4), (24, 10), (24, 16),
            (34, 5), (34, 10), (34, 16), (43, 6), 
            (43, 11), (43, 15), (55, 8), (55, 14)
        ]

    def assign_data_to_foot(self, data_from_sensors:list) -> np.ndarray:
        """
        Assign data to corresponding sensor positions on the insole grid using BFS.\n
        data_from_sensors : List of sensor values to be mapped.
        Returns the updated insole grid with assigned sensor data.
        """
        rows, cols = self.my_right_foot.shape
        for r in range(rows):
            for c in range(cols):
                if self.my_right_foot[r][c] == 0:
                    self.my_right_foot[r][c] = -1 # Label the non-sensor area as "-1" instead for this use
        foot = self.my_right_foot.copy()
        for i, (r, c) in enumerate(self.sensor_positions):
            foot[r][c] = data_from_sensors[i] # Assign the value to point from each group
            self.bfs(foot, r, c) # Spread the value to surrounding sensor area
        return foot

    def bfs(self, grid:np.ndarray, start_r:int, start_c:int):
        """
        Perform Breadth First Search(BFS) to spread sensor data to adjacent areas that was label as "2".\n
        grid : Insole grid with sensor data\n
        start_r, start_c : Starting point of the BFS
        """
        rows, cols = grid.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Move 4 directions: up,down,left,right(can be 8 directions as user desire)
        queue = deque([(start_r, start_c)]) # Can use queue instead of double ended queue
        visited = set((start_r, start_c)) # To check if we already visited that area
        value = grid[start_r, start_c]
        while queue:
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    if grid[nr][nc] == 1: # Skip if it's non-sensor area
                        continue
                    if grid[nr][nc] == 2: # Spread the sensor value
                        grid[nr, nc] = value
                        queue.append((nr, nc))
                        visited.add((nr, nc)) # Add that point to continue the spread

    def bilinear_interpolation(self, grid:np.ndarray, iterations:int) -> np.ndarray:
        """
        Smooth the pressure distribution using bilinear interpolation.\n
        Simple explanation: Sensor values are spread to adjacent areas(no need to be the sensor areas)\n, and areas between different sensor values are assigned the average of surrounding cells. This process repeats for the given iterations.\n
        Please see the example smoothed grid in README.md\n
        grid : Insole grid with sensor data
        iterations : Number of smoothing iterations
        Returns the smoothed grid.
        """
        rows, cols = grid.shape
        for _ in range(iterations):
            new_grid = grid.copy()
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] == 1:
                        sum = 0
                        neighbor_sum = 0
                        for dr in [-1, 0, 1]: # Move 8 direction
                            for dc in [-1, 0, 1]:
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < rows and 0 <= nc < cols and not (dr == 0 and dc == 0) and grid[nr][nc] != -1 and grid[nr][nc] != 1:
                                    neighbor_sum += grid[nr][nc] # Sum value of the applicable surrounding areas
                                    sum += 1
                        if sum > 0:
                            new_grid[r][c] = (neighbor_sum / sum) # Find the average
            grid = new_grid
        return grid

    def generate_insole_heatmap(self, data_from_sensors:list) -> np.ndarray:
        """
        This function is for generating the insole heatmap by combining all needed function
        data_from_sensors : List of sensor values to be mapped.
        Returns the final updated insole grid with assigned sensor data.
        """
        result = self.assign_data_to_foot(data_from_sensors)
        result = self.bilinear_interpolation(result, 10)
        return result

class HeatmapWidget(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Initialize the main window and the heatmap with real-time pressure distribution.\n
        Also sets up the time series plot for sensor data and starts the update timer.
        """
        super().__init__()

        global start_time
        start_time = time.time() # Record the start time for time series plotting

        self.insole_model = InsoleModel() # Initialize the insole model

        # Initialize data storage for each sensor's time series
        self.data_storage = [[] for _ in range(16)]  # 100 data points for each sensor
        self.time_storage = [[] for _ in range(16)]  # Corresponding timestamps for each sensor

        # Set up the window layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QHBoxLayout(self.central_widget)

        # Create layout for the heatmap
        self.heatmap_layout = QtWidgets.QVBoxLayout()

        # Create the heatmap canvas
        self.canvas = FigureCanvas(plt.Figure())
        self.heatmap_layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)

        # Add heatmap layout to the main layout
        self.main_layout.addLayout(self.heatmap_layout)

        # Adjust margins for the heatmap plot
        self.canvas.figure.subplots_adjust(left=-0.5, right=0.9, top=0.9, bottom=0.1)

        self.colorbar = None # Colorbar for heatmap

        # Create the time series plot widget and add to the main layout
        self.time_series_plot = pg.PlotWidget()
        self.main_layout.addWidget(self.time_series_plot)

        # Set window properties
        self.setWindowTitle("Real-time Foot Pressure Heatmap")
        self.setGeometry(100, 100, 1400, 600)  # Adjust the window size for better fit

        # Set timer for updating the heatmap
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # Update every 100 milliseconds
        self.timer.timeout.connect(self.update_heatmap)
        self.timer.start()

        self.setup_plot() # Set up the time series plot

    def sub_data(self, mqtt_data:list):
        """
        Callback function for receiving data from the MQTT subscriber.\n
        mqtt_data : List of sensor values received from MQTT broker
        """
        self.latest_data = mqtt_data

    def update_heatmap(self):
        """
        Update the heatmap with the latest sensor data and redraw it.\n
        Repeat every 100ms.
        """
        if self.latest_data is not None:
            # Rearrange sensor data for heatmap mapping
            sensor_data = [
                self.latest_data[6],  self.latest_data[7],  self.latest_data[5],  self.latest_data[8],
                self.latest_data[15], self.latest_data[4],  self.latest_data[11], self.latest_data[14],
                self.latest_data[0],  self.latest_data[10], self.latest_data[13], self.latest_data[1],
                self.latest_data[9],  self.latest_data[12], self.latest_data[3],  self.latest_data[2]
            ]
            foot_heatmap = self.insole_model.generate_insole_heatmap(sensor_data) # Generate the heatmap

            # Replace non-sensor areas with NaN for proper visualization
            foot_heatmap_with_background = np.where(self.insole_model.my_right_foot == -1, np.nan, foot_heatmap)

            self.ax.clear() # Clear the previous heatmap
            extent = [0, 78, 0, 235] # Set the physical extent of the plot

            cmap = plt.cm.jet # Define colormap for the heatmap
            cmap.set_bad(color='white') # Set color for NaN areas
            cmap.set_under(color='lightblue') # Set color for underflow values

            # Plot the heatmap
            img = self.ax.imshow(foot_heatmap_with_background, cmap=cmap, interpolation='none', extent=extent, vmin=0, vmax=4096)
            
            # Add titles, labels, and ticks
            title_fontsize = 18
            label_fontsize = 14
            tick_fontsize = 12
            self.ax.set_title('Insole Pressure Distribution (Real-Time)', pad=24, fontsize=title_fontsize)
            self.ax.set_xticks([0, 78])
            self.ax.set_yticks([0, 235])
            self.ax.set_xticklabels(['0', '78'], fontsize=tick_fontsize)
            self.ax.set_yticklabels(['0', '235'], fontsize=tick_fontsize)
            self.ax.set_xlabel('X Coordinate (mm)', fontsize=label_fontsize)
            self.ax.set_ylabel('Y Coordinate (mm)', fontsize=label_fontsize)

            if self.colorbar is None:  # Create the colorbar only if it doesn't exist
                self.colorbar = self.canvas.figure.colorbar(img, ax=self.ax)
                self.colorbar.set_label('Pressure Value',labelpad=20,fontsize=label_fontsize)
            else:
                img.colorbar = self.colorbar  # Reuse the existing colorbar
                self.colorbar.update_normal(img)  # Update the colorbar with the new image

            self.canvas.draw() # Redraw the canvas with the updated heatmap

            self.update_time_series(self.latest_data) # Update the time series plot

    def setup_plot(self):
        """
        Set up the time series plot with initial empty curves for each sensor.\n
        Initialize data storage and set labels and titles.
        """ 
        self.curves = [] # Initialize empty list for collect the data
        self.data_storage = [[] for _ in range(16)]  # Initialize a list with 16 empty lists, one for each sensor's data
        self.time_storage = [[] for _ in range(16)]  # Corresponding timestamps for each sensor

        # Initialize curves for each sensor
        for i in range(16):
            curve = self.time_series_plot.plot(
                [], [], 
                pen=pg.mkPen(color=pg.intColor(i, 16), width=2),
                name=f'Sensor {i+1}' 
            )
            self.curves.append(curve)
        
        # Set the title and axis labels for the plot
        self.time_series_plot.setTitle("Time Series of Sensor Readings (16 Channels)", color='#FFF', size='26pt')
        labelStyle = {'color': '#FFF', 'font-size': '20pt'}
        self.time_series_plot.setLabel('left', 'Value', units='', **labelStyle)
        self.time_series_plot.setLabel('bottom', 'Time (s)', units='', **labelStyle)

         # Define Y-axis ticks
        y_ticks = [(0, '0'), (1000, '1000'), (2000, '2000'), (3000, '3000'), (4096, '4096'), (5000, '5000')]
        self.time_series_plot.getAxis('left').setTicks([y_ticks])

        # Add an infinite line at value 4096 to indicate maximum
        line = pg.InfiniteLine(pos=4096, angle=0, pen=pg.mkPen(color='r', width=2, style=pg.QtCore.Qt.DashLine))
        self.time_series_plot.addItem(line)
        
         # Create a custom legend for the plot
        if not hasattr(self, 'legend_layout'):
            self.legend_layout = pg.GraphicsLayout(border=(100, 100, 100))
            self.time_series_plot.scene().addItem(self.legend_layout)
            
            # Position and size of the legend layout
            self.legend_layout.setPos(80, 40)
            self.legend_layout.setFixedHeight(30)

            # Add the sensor legends in two horizontal lines
            for i in range(8):
                label = pg.LabelItem(f"Sensor {i+1}", color=pg.intColor(i, 16))
                self.legend_layout.addItem(label, row=0, col=i)
            for i in range(8, 16):
                label = pg.LabelItem(f"Sensor {i+1}", color=pg.intColor(i, 16))
                self.legend_layout.addItem(label, row=1, col=i-8)
 
    def update_time_series(self, new_data:list):
        """
        new_data : Insole data
        This function update the time series graph within time interval(adjustable).
        """
        global start_time
        # The data is in form [:16] is data sensor the 17th is timestamp and the 18th is count
        timestamp = new_data[-2] - start_time # Extract the 17th element as the timestamp
        sensor_data = new_data[:16]  # Extract the first 16 elements as sensor data
        
        # Ensure the Y-axis only shows values between 0 and 4096 before updating the data
        self.time_series_plot.setYRange(0, 5000)
        
        # Update each sensor's curve with the new data
        for i, value in enumerate(sensor_data):
            self.data_storage[i].append(value) # Append new value
            self.time_storage[i].append(timestamp) # Append new timestamp
            
            """
            Maintain only the last 100 data points for each sensor.\n
            Since the data update every 100 ms, this means data will keep within 10 seconds.
            """
            if len(self.data_storage[i]) > 100:
                self.data_storage[i].pop(0) 
                self.time_storage[i].pop(0)
            
            # Update the curve
            self.curves[i].setData(self.time_storage[i], self.data_storage[i])

class UiSubscriberThread(QThread):
    subscribed_data = pyqtSignal(list) # Signal to emit received data
    
    def __init__(self, topic, broker_address:str, broker_port:int):
        """
        Initialize the MQTT subscriber thread for receiving sensor data.\n
        topic : MQTT topic to subscribe to.
        broker_address : Address of the MQTT broker.
        broker_port : Port number of the MQTT broker.
        """
        QThread.__init__(self)
        self.topic = topic
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def __del__(self):
        """
        Stop the MQTT loop when the thread is deleted.
        """
        self.client.loop_stop()
        self.wait()
    
    def on_connect(self, client: mqtt.Client, userdata: any, flags: dict, rc: int):
        """
        Callback for MQTT connection.\n
        client : MQTT client instance.
        userdata : Custom user data.
        flags : Response flags.
        rc : Response code indicating the connection result.
        """
        print(f"Connected to MQTT Broker with result code {rc}")
        self.client.subscribe(self.topic) # Subscribe to the topic

    def on_message(self, client: mqtt.Client, userdata: any, msg: mqtt.MQTTMessage):
        """
        Callback for MQTT messages.\n
        client : MQTT client instance.
        userdata : Custom user data.
        msg : Received message.
        """
        payload = json.loads(msg.payload.decode()) # Decode the payload
        print(payload)
        self.subscribed_data.emit(payload) # Emit the received data as a signal
    
    def run(self):
        """
        Start the MQTT loop and connect to the broker.
        """
        self.client.connect(self.broker_address, self.broker_port, 60)
        self.client.loop_start()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    # Create the heatmap window
    window = HeatmapWidget()
    window.show()

    # Start the MQTT subscriber thread
    mqtt_thread = UiSubscriberThread(topic="data/json", broker_address="YOUR_MQTT_BROKER_IP", broker_port=1883)
    mqtt_thread.subscribed_data.connect(window.sub_data)
    mqtt_thread.start()

    app.exec()
