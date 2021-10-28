'''
Minimal example showing how to use pyqthgraph to make a 2D "image" plot
that is updated continuously like a video. For a super-basic example 
see surfacePlotExample.py; the code below is a little more elaborate.


Rob Campbell - SWC 2020
'''


import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg


## Create a smoothed random image
img = pg.gaussianFilter(np.random.normal(size=(200, 200)), (5, 5)) * 20 + 100

## Display the data
imview = pg.image(img)

# Remove the buttons beneath to histogram
imview.ui.roiBtn.hide()
imview.ui.menuBtn.hide()

# So the histogram does not bounce arond like crazy
imview.ui.graphicsView.autoPixelRange=False 
imview.ui.histogram.autoPixelRange=False 

updateTime = pg.ptime.time()
fps = 0
def updateData():
    global updateTime, fps
    ## Display the data
    img = pg.gaussianFilter(np.random.normal(size=(200, 200)), (5, 5)) * 20 + 100
    imview.setImage(img, autoLevels=False, autoHistogramRange=False) # Display new image and stop range from jumping around
    QtCore.QTimer.singleShot(1, updateData) # Recursive call here
    now = pg.ptime.time()
    fps2 = 1.0 / (now-updateTime)
    updateTime = now
    fps = fps * 0.9 + fps2 * 0.1
    imview.setWindowTitle('%0.1f fps (close window to stop)' % fps)


updateData()
    
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
