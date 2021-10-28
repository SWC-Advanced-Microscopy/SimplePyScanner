
'''
Makes a scrolling plot using pyqtgraph. 

Run from the command line as:
$ python scrolling_plot.py

'''


import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui




# Make some random data
t_data = np.random.randn(256)

# Make the plot window
win = pg.GraphicsLayoutWidget(show=True)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)


# Add a set of axes and plot into them
t_axes = win.addPlot()
t_plot = t_axes.plot(t_data,pen='y')


# Define a function that will update the plot
ptr=0
def update():
    global t_data, ptr
    t_data[:-1] = t_data[1:]  # shift data in the array one sample left

    t_data[-1] = np.random.normal() #add a new random number to the last value
    t_plot.setData(t_data)
    t_plot.setPos(ptr,0) #Through some unclear mechanism this scrolls the x axis
    ptr += 1



# Set up a timer that runs every 50 ms
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore,'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
