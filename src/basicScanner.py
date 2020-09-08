'''
 Basic no-frills scanning softwareDemonstration of simultaneous analog input and output


 Description:
  This code demonstrates the most simple possible way of driving a pair of galvo mirrors
  to produce a laser scan pattern that then be used to assemble an image of a sample.
  Image artifacts are not corrected and there is no easy way to change scan properties.
 
  Wiring instructions:
  - AO0 to your fast scan axis
  - AO1 to your slow scan axis
  - AI0 to your PMT or photodiode
 
  You may run this example by changing to the directory containing the file and
  running: python basicScanner.py

'''

import nidaqmx
from nidaqmx.constants import (AcquisitionType,RegenerationMode)
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

class basicScanner():

    # Data are pulled in at +/- this number of volts. You may need to tweak
    # this parameter for your detector
    detector_voltage_range = 1

    # The scan mirrors will be driven by a waveform that is +/- this number
    # of volts. A larger number produces a larger scan pattern. This is 
    # equivilent to "zooming out" in a conventional wide-field microscope.
    scan_amplitude = 1


    waveforms = []  # Will contain the x and y scanner waveforms
    im_size = 256   # Number of pixel rows and columns (square images)
    invert_signal = -1  # Set to -1 if using a non-inverting amp with a PMT

    # NI DAQ Task configuration
    dev_name = 'Dev1'      # The name of the DAQ device as shown in MAX
    sample_rate = 128E3     # Sample Rate in Hz
    num_samples_per_channel = [] #The length of the waveform
    
    h_task_ao = [] # DAQmx task handle for analog output
    h_task_ai = [] # DAQmx task handle for analog input


    # Properties associated with plotting
    _points_to_plot = []    # scalar defining how many points to plot at once
    _app = []               # QApplication stored here
    _win = []               # GraphicsLayoutWidget stored here
    _plot = []              # plot object stored here
    _curve = []             # pyqtgraph plot object


    def __init__(self, autoconnect=False):

        if autoconnect:
            self.set_up_tasks()



    def set_up_tasks(self):
        '''
        Creates AI and AO tasks. Builds a waveform that is played out through AO using
        regeneration. Connects AI to a callback function to handling plotting of data.
        '''

        # * Create two separate DAQmx tasks for the AI and AO
        self.h_task_ao = nidaqmx.Task('simplescannerao')
        self.h_task_ai = nidaqmx.Task('simplescannerai')


        # * Connect to analog input and output voltage channels on the named device
        self.h_task_ao.ao_channels.add_ao_voltage_chan( '%s/ao0:1' % self.dev_name)
        self.h_task_ai.ai_channels.add_ai_voltage_chan( '%s/ai0' % self.dev_name)


        self.generateScanWaveforms() # This populates the waveforms property
        '''
        SET UP ANALOG INPUT
        '''

        # * Configure the sampling rate and the number of samples
        self.h_task_ai.timing.cfg_samp_clk_timing(self.sample_rate, \
                                    source= '/%s/ao/SampleClock' % self.dev_name, \
                                    samps_per_chan=self._points_to_plot, \
                                    sample_mode=AcquisitionType.CONTINUOUS)

        # NOTE: must explicitly set the input buffer so that it's a multiple
        # of the number of samples per frame. Setting the samples per channel 
        # (above) does not achieve this.
        self.h_task_ai.in_stream.input_buf_size = self._points_to_plot * 2

        # * Register a a callback funtion to be run every N samples
        self.h_task_ai.register_every_n_samples_acquired_into_buffer_event(self._points_to_plot, self._read_and_display_last_frame)


        '''
        SET UP ANALOG OUTPUT
        '''


        # * Configure the sampling rate and the number of samples
        #   C equivalent - DAQmxCfgSampClkTiming
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


        # * Build and write the waveforms
        self.h_task_ao.write(self.waveforms, timeout=2)



        '''
        Set up the triggering
        '''
        # The AO task should start as soon as the AI task starts.
        #   More details at: "help dabs.ni.daqmx.Task.cfgDigEdgeStartTrig"
        #   DAQmxCfgDigEdgeStartTrig
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgdigedgestarttrig/
        self.h_task_ao.triggers.start_trigger.cfg_dig_edge_start_trig( '/' + self.dev_name + '/ai/StartTrigger' )

        # Note that now the AO task must be started before the AI task in order for the synchronisation to work


    def generateScanWaveforms(self):
        '''
        This method builds simple ("unshaped") galvo waveforms and stores them in the self.waveforms property.
        "shaped" waveforms would be those that have some sort of smoothed deceleration at the mirror 
        turn-arounds to help increase frame rate and improve scanning accuracy. 
        '''

        yWaveform = np.linspace(self.scan_amplitude, -self.scan_amplitude, self.im_size**2)

        # The X waveform goes from +scan_amplitude to -scan_amplitude over the course of one line.
        xWaveform = np.linspace(-self.scan_amplitude, self.scan_amplitude, self.im_size) # One line of X

        # Repeat the X waveform "imSize" times in order to build a square image
        xWaveform = np.tile(xWaveform, self.im_size)

        # Assemble the two waveforms
        self.waveforms = np.stack((xWaveform, yWaveform));

        self._points_to_plot = len(yWaveform)

        # Report frame rate to screen
        print('Scanning with a frame size of %d by %d pixels at %0.2f frames per second. %d samples per frame.\n' % \
             (self.im_size, self.im_size, self.sample_rate/self._points_to_plot,self._points_to_plot) );


    def setup_plot(self):
        # Set up pyqtgraph plot window
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
        data = self.h_task_ai.read(number_of_samples_per_channel=self._points_to_plot)
        self._plot.setImage(np.array(data).reshape(self.im_size,self.im_size), autoLevels=False, autoHistogramRange=False)
        return 0


    def start_acquisition(self):
        if not self._task_created():
            return

        self.setup_plot()
        self.h_task_ao.start()
        self.h_task_ai.start() # Starting this task triggers the AO task


    def stop_acquisition(self):
        if not self._task_created():
            return

        self.h_task_ai.stop()
        self.h_task_ao.stop()

    def close_tasks(self):
        if not self._task_created():
            return

        self.h_task_ai.close()
        self.h_task_ao.close()

    # House-keeping methods follow
    def _task_created(self):
        '''
        Return True if a task has been created
        '''

        if isinstance(self.h_task_ao,nidaqmx.task.Task) or isinstance(self.h_task_ai,nidaqmx.task.Task):
            return True
        else:
            print('No tasks created: run the set_up_tasks method')
            return False



if __name__ == '__main__':
    print('\nRunning demo for basicScanner\n\n')
    SCANNER = basicScanner()
    SCANNER.set_up_tasks()
    SCANNER.start_acquisition()
    input('press return to stop')
    SCANNER.stop_acquisition()
    SCANNER.close_tasks()
