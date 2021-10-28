'''
Minimal example showing how to use pyqthgraph to make a 2D "image" plot
This is achieved using ImageView, which is a high-level widget for 
displaying and analyzing 2D or 3D data. The ImageView provides:

  1. A zoomable region (ViewBox) for displaying the image
  2. A combination histogram and gradient editor (HistogramLUTItem) for
     controlling the visual appearance of the image
  3. A timeline for selecting the currently displayed frame (for 3D data only). (not used here)
  4. Tools for very basic analysis of image data (see ROI and Norm buttons)


Rob Campbell - SWC 2021
'''



import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui



## Create a smoothed random image
img = pg.gaussianFilter(np.random.normal(size=(200, 200)), (5, 5)) * 20 + 100
pg.image(img)

    
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
