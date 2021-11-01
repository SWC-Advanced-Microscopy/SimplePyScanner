'''
 Exercise in which you build no-frills scanning software.

 image_scanner


 Description:
  The exercise demonstrates the most simple possible way of driving a pair of galvo mirrors
  to produce a laser scan pattern that then be used to assemble an image of a sample.
  Image artifacts are not corrected and there is no easy way to change scan properties.
 
  Instructions:
  - AO0 to your fast scan axis
  - AO1 to your slow scan axis
  - AI0 to your PMT or photodiode
  - You will need to edit the lines at the locations marked by the string ### EDIT
  - There may be hints and instructions around those lines.
  - Read through 
  - HINT -- if you get stuck look at waveformTester.py and your previous exercises

  Run by changing to the directory containing the file and calling: 
  python image_scanner.py

'''


import nidaqmx
from nidaqmx.constants import (AcquisitionType,RegenerationMode)
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

class image_scanner():

    # Data are pulled in at +/- this number of volts. You may need to tweak
    # this parameter for your detector
    detector_voltage_range = 1

    # The scan mirrors will be driven by a waveform that is +/- this number
    # of volts. A larger number produces a larger scan pattern. This is 
    # equivilent to "zooming out" in a conventional wide-field microscope.
    scan_amplitude = 1


    waveforms = []  # Will contain the x and y scanner waveforms
    im_size = 256   # Number of pixel rows and columns (square images)


    # NI DAQ Task configuration
    dev_name = ''          ### EDIT -- change to your DAQ
    sample_rate = 96E3     # Sample Rate in Hz
    num_samples_per_channel = [] #The length of the waveform
    
    h_task_ao = [] # DAQmx task handle for analog output
    h_task_ai = [] # DAQmx task handle for analog input


    # Properties associated with pyqtgraph plotting
    _points_to_plot = []    # scalar defining how many points to plot at once
    _app = []               # QApplication stored here
    _win = []               # GraphicsLayoutWidget stored here
    _plot = []              # plot object stored here


    def __init__(self, autoconnect=False):

        if autoconnect:
            self.set_up_tasks()



    def set_up_tasks(self):
        '''
        Creates AI and AO tasks. Builds a waveform that is played out through AO using
        regeneration. Connects AI to a callback function to handling plotting of data.
        '''

        # * Create two separate DAQmx tasks for the AI and AO
        self.h_task_ao =  ### EDIT -- create a DAQmx task
        self.h_task_ai =  ### EDIT -- create a DAQmx task


        # * Connect to analog input and output voltage channels on the named device
        self.h_task_ao.ao_channels.add_ao_voltage_chan( '%s/ao0:1' % self.dev_name)
        self.h_task_ai.ai_channels. ### EDIT -- complete to add one AI voltage channel sampling AI0


        self.generateScanWaveforms() # YOU WILL NEED TO EDIT THIS METHOD
        '''
        SET UP ANALOG INPUT
        '''

        # * Configure the sampling rate and the number of samples
        ###EDIT -- Set the sample_mode for continuous acquisition 
        self.h_task_ai.timing.cfg_samp_clk_timing(self.sample_rate, \
                                    source= '/%s/ao/SampleClock' % self.dev_name, \
                                    samps_per_chan=self._points_to_plot, \
                                    sample_mode=)


        # NOTE: must explicitly set the input buffer so that it's a multiple
        # of the number of samples per frame. Setting the samples per channel 
        # (above) does not achieve this.
        self.h_task_ai.in_stream.input_buf_size = self._points_to_plot * 2

        # * Register a a callback function to be run every N samples
        ### EDIT: Set up the callback function
        '''
            - Call the correct method of self.h_task_ai to register a callback function for every every n samples acquired
            - Tell the function how often to run. Think what is a logical point at which to update the image. In other 
              words, every how many samples? If you are lost look in the generateScanWaveforms method.
            - Which method should you call? Hint: it's already largely written . 

        '''
        self.h_task_ai.


        '''
        SET UP ANALOG OUTPUT
        '''


        # * Configure the sampling rate and the number of samples
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
        #   https://nidaqmx-python.readthedocs.io/en/latest/timing.html
        self.h_task_ao.timing.cfg_samp_clk_timing(rate = self.sample_rate, \
                                               samps_per_chan=self._points_to_plot, \
                                               sample_mode = AcquisitionType.CONTINUOUS)


        # * Do allow sample regeneration: i.e. the buffer contents will play repeatedly (cyclically).
        # http://zone.ni.com/reference/en-XX/help/370471AE-01/mxcprop/attr1453/
        # For more on DAQmx write properties: http://zone.ni.com/reference/en-XX/help/370469AG-01/daqmxprop/daqmxwrite/
        # For a discussion on regeneration mode in the context of analog output tasks see:
        # https://forums.ni.com/t5/Multifunction-DAQ/Continuous-write-analog-voltage-NI-cDAQ-9178-with-callbacks/td-p/4036271
        self.h_task_ao.out_stream.regen_mode = RegenerationMode.ALLOW_REGENERATION



        # * Set the size of the output buffer
        #   C equivalent - DAQmxCfgOutputBuffer
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxcfgoutputbuffer/
        #self.h_task.cfgOutputBuffer(num_samples_per_channel);


        # * Write the two waveforms to the AO buffer
        self.h_task_ao. ###EDIT



        '''
        Set up the triggering
        '''
        # In order for the scanning software to work, the AO and AI tasks must start simultaneously. 
        # If this is the case then we can assume that, if the mirrors behaved perfectly, the photodiode 
        # signal at AI0 must reflect signal from the beam location defined by AO0 and AO1. 
        # The following line of code must set the AO task to be triggered to start by the AI task. 
        # This, of course, also had to be done in the waveform tester...
        # http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgdigedgestarttrig/
        self.h_task_ao. ###EDIT

        # Note that:
        # - The AO task must be started before the AI task in order for the synchronization to work.
        # - The start_acquisition and stop_acquisition methods are already written. 



    def generateScanWaveforms(self):
        '''
        This method builds simple galvo waveforms and stores them in the self.waveforms property.
        '''

        yWaveform = np.linspace()  ###EDIT -- complete this line using self.im_size and self.scan_amplitude

        # ###EDIT -- generate the xWaveform
        xWaveform = 


        # ###EDIT -- waveformTester.py played a single analog output waveform. Here we will need to play yWaveform 
        # out of AO1 and xWaveform out of AO0. To achieve this, NIDAQmx expects a matrix to be fed into the buffer. 
        # The rows are samples are and the columns are channels. Therefore you need generate a 2D matrix where the 
        # first column is xWaveform and the second column is yWaveform. Hint: stack
        self.waveforms =

        # Report frame rate to screen
        self._points_to_plot = len(yWaveform)
        print('Scanning with a frame size of %d by %d pixels at %0.2f frames per second. %d samples per frame.\n' % \
             (self.im_size, self.im_size, self.sample_rate/self._points_to_plot,self._points_to_plot) );


    def setup_plot(self):
        # Set up pyqtgraph plot window. Nothing to edit here. 
        self._app = QtGui.QApplication([])
        self._win = QtGui.QMainWindow()
        self._win.resize(800,800) # Make window 800 by 800 pixels
        pg.setConfigOptions(antialias=True)
        self._plot = pg.ImageView()
        self._win.setCentralWidget(self._plot)
        self._win.show()

        # Remove the buttons beneath to histogram
        self._plot.ui.roiBtn.hide()
        self._plot.ui.menuBtn.hide()


    def _read_and_display_last_frame(self,tTask, event_type, num_samples, callback_data):
        # Callback function that extract data and update plots
        # NOTE: This function should plot data from one frame. 

        data = self.h_task_ai. ###EDIT -- read the correct number of samples from the buffer

        im = ###EDIT -- convert the 1D verctor into a 2D image
        self._plot.setImage( im, autoLevels=False, autoHistogramRange=False)

        return 0 #callbacks must return 0


    def start_acquisition(self):
        # Nothing to do here
        if not self._task_created():
            return

        self.setup_plot()
        self.h_task_ao.start()
        self.h_task_ai.start() # Starting this task triggers the AO task


    def stop_acquisition(self):
        # Nothing to do here
        if not self._task_created():
            return

        self.h_task_ai.stop()
        self.h_task_ao.stop()

    def close_tasks(self):
        # Nothing to do here
        if not self._task_created():
            return

        self.h_task_ai.close()
        self.h_task_ao.close()

    # House-keeping methods follow
    def _task_created(self):
        # Nothing to do here
        '''
        Return True if a task has been created
        '''

        if isinstance(self.h_task_ao,nidaqmx.task.Task) or isinstance(self.h_task_ai,nidaqmx.task.Task):
            return True
        else:
            print('No tasks created: run the set_up_tasks method')
            return False




if __name__ == '__main__':
    print('\nRunning demo for image_scanner\n\n')
    SCANNER = image_scanner()
    SCANNER.set_up_tasks()
    SCANNER.start_acquisition()
    input('press return to stop')
    SCANNER.stop_acquisition()
    SCANNER.close_tasks()
