
'''
 Generate and test various galvo waveforms

 waveformTester


 Description:
 This is a tutorial class to explore the scan waveform. Parameters are set by
 editing the properties. The class drives a scan mirror with a sinusoidal or
 sawtooth waveform and shows how well the mirror can keep up by plotting the
 feedback signal as a function of the command signal. The left plot shows a
 sinusoidal white trace overlaid by a red trace. The white is the command signal
 and the red the position signal. The right plot shows the position signal as
 a function of the command signal. Frequency of the waveform is displayed
 at the command line.


 Wiring Instructions
 * Hook up AO0 to the X galvo command (input) voltage terminal.
 * Wire up the DAQ using a T piece to copy AO0 to AI0
 * Connect AI1 to the X galvo position (output) terminal.


 To run from a Python command prompt:
 cd to code directory and start Python then:
   from waveformTester import waveformTester
   S=waveformTester()       # To connect to Dev1.
   S=waveformTester('Dev3') # To connect to a named device ID
   You can stop acquisition by closing the window.


 To start from a system command prompt:
 cd to code directory then:
 python waveformTester.py
 You can stop acquisition by closing the window or pressing return



 NOTE with USB DAQs: you will get error -200877 if the AI buffer is too small.


 Things try:
 The scanners have inertia so their ability to follow the command waveform will depend upon
 its shape and frequency. Let's try changing the frequency. Close the figure window (take
 screenshot first if you want to compare before and after) and edit the "sample_rate" property.
 Increase it to, say 128E3. Re-start the object. Notice the larger lag between the position
 and command and how this is reflected in the phase (X/Y) plot "opening up".

 Let's now try having fewer samples per cycle. Stop, set "pixels_per_line" to 128, and restart.
 If your scanners can't keep up, try a larger value. At 128 samplesPerLine and 128 kHz sample
 rate the scanner runs at 1 kHz. There will be a big lag now. If your scanners will keep up, you
 can try lines as short as about 32 pixels, which is 4 kHz. Don't push beyond this in case the
 scanners can't cope. Also, don't try such high frequencies with other command waveform shapes.

 Try a sawtooth waveform by modifying the waveform_type property. Start with a frequency below 500 Hz
 then try higher frequency (e.g. 2 kHz). How well do the scanners follow the command signal?


 See Also:
 basicScanner.py
'''

import nidaqmx
from nidaqmx.constants import (AcquisitionType,RegenerationMode)
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

class waveformTester():

    # Define properties that we will use for the acquisition.

    # These properties are common to both the AO and AI tasks
    dev_name = 'Dev1'
    sample_rate = 32E3   # The sample rate at which the board runs (Hz)
    waveform_type='sawtooth' # Waveform shape. Valid values are: 'sine', 'sawtooth'

    # These properties are specific to scanning via the AO lines
    galvo_amplitude =  4     # Scanner amplitude (defined as peak-to-peak/2)
    pixels_per_line =  256   # Number pixels per line for a sawtooth waveform (for sine wave this defines wavelength)
    num_reps_per_acq = 10    # How many times to repeat this waveform in one acquisiion

    ao_task = []  # The AO task handle will be kept here
    waveform = [] # The scanner waveform will be stored here

    # Properties for the analog inputs
    ai_task = [] #The AI task handle will be kept here


    # These properties hold information relevant to the plot window
    _app = []
    _win = []
    _main_plot = [] # Handle for the main axes
    _phase_plot = [] # Handle fo the plot of AI1 as a function of AI0
    _plt_ao0 = [] # AO0 plot data
    _plt_ai0 = [] # AI0 plot data
    _plt_phase  = [] # AO0 vs AO1 plot data

    _read_number = 0 # counter for the number of times the DAQmx callback is run




    def __init__(self,dev_name=''):

        # Optionally replace device name if needed
        if 'Dev' in dev_name:
            self.dev_name = dev_name

        # Build the figure window
        self.build_figure_window()

        # Call a method to connect to the DAQ. If the following line fails, the Tasks are
        # cleaned up gracefully and the object is deleted. This is all done by the method
        # call and by the destructor
        self.connect_to_daq()


        self.start()
        print('Close figure to quit acquisition')
    # close constructor


    def __del__(self):
        print('Running destructor')
        #if ~isempty(self.hFig) && isvalid(self.hFig)
        #    self.hFig.delete #Closes the plot window
        self.stop() # Call the method that stops the DAQmx tasks
    #close destructor


    def connect_to_daq(self):
        # First generate scan waveforms, as they properties will affect some variables, such as
        # buffer sizes.

        self.generate_scan_waveform() #This will populate the waveform property
        l_wav = len(self.waveform)

        print('Connecting to DAQ')

        # Create separate DAQmx tasks for the AI and AO
        self.ai_task = nidaqmx.Task('signalReceiver')
        self.ao_task = nidaqmx.Task('waveformMaker')

        #  Set up analog input and output voltage channels, digitizing over +/- maxV Volts
        # Channel 0 is the recorded copy of the AO signal. Channel 1 is the scanner feedback.
        maxV=10
        self.ai_task.ai_channels.add_ai_voltage_chan(self.dev_name+'/ai0:1', min_val=-maxV, max_val=maxV)
        self.ao_task.ao_channels.add_ao_voltage_chan(self.dev_name+'/ao0', min_val=-maxV, max_val=maxV)


        # * Set up the AI task

        # Configure the sampling rate and the number of samples so that we are reading back data
        # at the end of each waveform

        # Set timing and use AO clock for AI
        buf_size_scale_factor = 5
        self.ai_task.timing.cfg_samp_clk_timing(self.sample_rate, \
                            source= '/%s/ao/SampleClock' % self.dev_name, \
                            samps_per_chan=l_wav*buf_size_scale_factor, \
                            sample_mode=AcquisitionType.CONTINUOUS)

        # NOTE: must explicitly set the input buffer so that it's a multiple
        # of the number of samples per frame. Setting the samples per channel
        # (above) does not achieve this.
        self.ai_task.in_stream.input_buf_size = l_wav*buf_size_scale_factor


        # Call an anonymous function to read from the AI buffer and plot the images once per frame
        print(self.sample_rate)
        print('Running callback every %0.2f seconds' % (l_wav/self.sample_rate) )
        self.ai_task.register_every_n_samples_acquired_into_buffer_event(l_wav, self.read_and_display_data)


        # * Set up the AO task
        # Set the size of the output buffer
        self.ao_task.timing.cfg_samp_clk_timing(self.sample_rate, \
                sample_mode=AcquisitionType.CONTINUOUS, \
                samps_per_chan=len(self.waveform))


        # Allow sample regeneration (buffer is circular)
        self.ao_task.out_stream.regen_mode = RegenerationMode.ALLOW_REGENERATION


        # Write the waveform to the buffer with a 5 second timeout in case it fails
        self.ao_task.write(self.waveform, timeout=5)


        # Configure the AO task to start as soon as the AI task starts
        self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig( '/' + self.dev_name + '/ai/StartTrigger' )
    # close connect_to_daq


    def build_figure_window(self):
        print("Building figure window")
        self._app = QtGui.QApplication([])
        self._win = pg.GraphicsLayoutWidget(show=True)

        # Make two subplots
        self._main_plot = self._win.addPlot() #Waveforms will go here
        self._phase_plot = self._win.addPlot() #Phase relationship between waveforms


        # Declare the plot items
        self._main_plot.addLegend()
        self._plt_command = self._main_plot.plot(pen='w',name='AI0 (command)')
        self._plt_feedback = self._main_plot.plot(pen='r',name='AI1 (feedback)')
        self._plt_phase = self._phase_plot.plot(pen=pg.mkPen('y', width=3))

        # Set some general plot properties such as labels
        self._main_plot.setYRange(-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15)
        self._main_plot.getAxis('left').setLabel('Voltage (V)')
        self._main_plot.getAxis('bottom').setLabel('Time')
        self._phase_plot.getAxis('left').setLabel('feedback')
        self._phase_plot.getAxis('bottom').setLabel('command')
        self._phase_plot.setYRange(-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15)
        self._phase_plot.setXRange(-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15)

        # Set titles
        self._main_plot.setTitle('Command and feedback waveforms')
        self._phase_plot.setTitle('Phase plot')

        # Add grids
        self._main_plot.showGrid(x = True, y = True, alpha = 0.3)
        self._phase_plot.showGrid(x = True, y = True, alpha = 0.3)

        # Quit if user closes window
        self._app.setQuitOnLastWindowClosed(False)
        self._app.lastWindowClosed.connect(self.__del__)

        # Display the plot
        self._win.show()
    #close build_figure_window


    def start(self):
        # This method starts acquisition on the AO then the AI task.
        # Acquisition begins immediately since there are no external triggers.
        print('Starting the scanning AI and AO tasks')
        self.ao_task.start()
        self.ai_task.start()
    #close start


    def stop(self):
        # Stop the AI and then AO tasks
        print('Stopping the scanning AI and AO tasks')
        self.ai_task.stop()
        self.ao_task.stop()
    #close stop


    def generate_scan_waveform(self):
        # This method builds a simple ("unshaped") galvo waveform and stores it in the self.waveform

        if self.waveform_type == 'sawtooth':
            print('Generating a sawtooth')
            # The X waveform goes from +galvo_amplitude to -galvo_amplitude over the course of one line:
            xWaveform = np.linspace(-self.galvo_amplitude, self.galvo_amplitude, self.pixels_per_line)

            # Repeat the X waveform a few times to ease visualisation on-screen
            xWaveform = np.tile(xWaveform, self.num_reps_per_acq)
            self.waveform = xWaveform; # Assign to the waveform property which gets written to the DAQ

        elif self.waveform_type == 'sine':
            print('Generating a sine wave')
            # sine wave
            self.waveform = self.galvo_amplitude *  np.sin(np.linspace(-np.pi*self.num_reps_per_acq, \
                                                            np.pi*self.num_reps_per_acq, \
                                                            self.pixels_per_line*self.num_reps_per_acq))

        print('Generated a waveform of length %d and a line period of %0.3f ms (%0.1f Hz)' % \
               (self.pixels_per_line, self.line_period()*1E3, 1/self.line_period()))
    #close generate_scan_waveform


    def read_and_display_data(self,tTask, event_type, num_samples, callback_data):
        # This callback method is run each time data have been acquired.

        if self.ai_task.in_stream.avail_samp_per_chan < 1:
            print('No samples to read in input buffer')
            return 0


        data = self.ai_task.read(number_of_samples_per_channel=len(self.waveform))

        ## TODO -- update label text to show read number
        ## Updating the window title too often seems to lock the GUI on Win10
        #self._win.setWindowTitle()
        self._read_number += 1
        # This is not allowed: threading problem
        #self._main_plot.titleLabel.setText('Plot update #%d' % self._read_number)


        self._plt_command.setData(data[0])
        self._plt_feedback.setData(data[1])
        self._plt_phase.setData(data[0],data[1])

        return 0 # The callback must return 0
    #close read_and_display_data


    def line_period(self):
        if len(self.waveform)==0:
            LP=[]
        else:
            LP = len(self.waveform) / (self.sample_rate*self.num_reps_per_acq)

        return LP
    #close line_period

#close class waveformTester





if __name__ == '__main__':
    W=waveformTester()
    input('Press return to stop\n')

