import numpy as np
import pyqtgraph as pg


'''
    scrolling_plotter

    This example class demonstrates why object-oriented programming is useful
    in a data acquisition scenario. Imagine that the randomly generated trace
    arises from a DAQ device sampling an input stream.

    Example
    
    import scrolling_plotter

    # Make a plot and manipulate it
    s=scrolling_plotter.scrolling_plotter()
    s.set_color('c')
    s.update_interval(25)
    s.stop()
    s.start()

    # Add a second plot
    s2=scrolling_plotter.scrolling_plotter()
    s2.max_markers_plot=500
    s2.max_markers_plot=25
    s2.set_color('g')


    Rob Campbell - SWC 2021

    Also see:
    scrolling_plotter.py pyqgraph example
'''


class scrolling_plotter():

    data = [] # The data to be plotted
    win = []  # pyqtgraph plot window
    axes = [] # pyqtgraph plot axes
    curve = [] # pyqtgraph plotted data object
    timer = [] # QtCore timer goes here

    ptr = 0   # counter used to shift the x axis of the plot

    max_markers_plot = 256


    def __init__(self):
        # Generate a data point
        self.data = np.random.randn(1)

        # Create the plot
        self.win = pg.GraphicsLayoutWidget(show=True)
        pg.setConfigOptions(antialias=True)
        self.axes = self.win.addPlot()
        self.curve = self.axes.plot(self.data,pen='y')

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)
    # close constructor


    def update_plot(self):
        # Add a point to the end up to a maximum. Allow for the 
        # possibility that the maximum can change
        self.data = np.append(self.data,np.random.randn())
        self.data = self.data[-self.max_markers_plot:]

        # update the plot
        self.curve.setData(self.data)
        self.curve.setPos(self.ptr,0)
        self.ptr += 1
    #close update_plot


    # The folowing methods are supposed to be used interactively by the user
    def stop(self):
        # Stop scrolling
        self.timer.stop()
    #close stop


    def start(self):
        # Start scrolling
        self.timer.start()
    #close start


    def update_interval(self,interval=50):
        # Change the update interval
        self.timer.start(interval)
    #close update_interval


    def set_color(self,color='y'):
        # Set color using any accepted color value of pg.mkPen
        self.curve.setPen(pg.mkPen(color))
    #close set_color

#close scrolling_plotter
