
'''
 Generate and test various galvo waveforms

 waveformTester


 Description:
 This is a tutorial class to explore the scan waveform. Parameters are set by editing the properties.


 Instructions
 * Hook up AO0 to the galvo command (input) voltage terminal.
 * Wire up the rack to copy AO0 to AI0
 * Connect AI1 to the galvo position (output) terminal.

 To run from a Python command prompt:
 * cd to code directory
 * from waveformTester import waveformTester
 * Run: "S=waveformTester()" to connect to Dev1. If your device has a different ID
   you may run: "S=waveformTester('Dev3')" (or whatever is the ID of the device)

 To start from a system command prompt:
 python waveformTester.py


 You will see a sinusoidal black trace overlaid by a red trace. The black is the command signal
 and the red the position signal. The blue sub-plot shows the position signal as a function of
 the command signal. Frequency of the waveform is displayed in the window title and at the
 command line.

 You can stop acquisition by closing the window.

 NOTE with USB DAQs: you will get error -200877 if the AI buffer is too small.


 Things try:
 The scanners have inertia so their ability to follow the command waveform will depend upon
 its shape and frequency. Let's try changing the frequency. Close the figure window (take
 screenshot first if you want to compare before and after) and edit the "sample_rate" property.
 Increase it to, say 128E3. Re-start the object. Notice the larger lag between the position
 and command and how this is reflected in the blue X/Y plot "opening up".

 Let's now try having fewer samples per cycle. Stop, set "pixels_per_line" to 128, and restart.
 If your scanners can't keep up, try a larger value. At 128 samplesPerLine and 128 kHz sample
 rate the scanner runs at 1 kHz. There will be a big lag now. If your scanners will keep up, you
 can try lines as short as about 32 pixels, which is 4 kHz. Don't push beyond this in case the
 scanners can't cope. Also, don't try such high frequencies with other command waveform shapes.

 Go back to 1 kHz and try different amplitudes. See how the lag is the same across amplitudes.

 Now let's explore AO/AI synchronisation. Set pixels_per_line to 128 and the sample rate to 128E3.
 All should look good. Try a range of different, but similar, sample rates. e.g. 117E3. Likely you
 will see a warning message and precession of the AI waveforms (this is relative to the AO).
 You can fix this by setting the AI and AO clocks to be shared as in the polishedScanner class.

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
    waveform_type='sine' # Waveform shape. Valid values are: 'sine', 'sawtooth'

    # These properties are specific to scanning via the AO lines
    galvo_amplitude =  3     # Scanner amplitude (defined as peak-to-peak/2)
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

        #  Set up analog input and output voltage channels, digitizing over +/- 5V
        # Channel 0 is the recorded copy of the AO signal. Channel 1 is the scanner feedback.
        self.ai_task.ai_channels.add_ai_voltage_chan(self.dev_name+'/ai0:1', min_val=-5, max_val=5)
        self.ao_task.ao_channels.add_ao_voltage_chan(self.dev_name+'/ao0', min_val=-5, max_val=5)


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
        self._main_plot = self._win.addPlot()
        self._plt_ao0 = self._main_plot.plot(pen='w',name='AO0')
        self._plt_ai0 = self._main_plot.plot(pen='r',name='AI0')

        self._main_plot.setYRange(-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15)
        self._main_plot.getAxis('left').setLabel('Voltage (V)')
        self._main_plot.getAxis('bottom').setLabel('Time (ms)')



        self._phase_plot = self._win.addPlot()
        self._plt_phase = self._phase_plot.plot(pen='b')

        self._phase_plot.getAxis('left').setLabel('AO0')
        self._phase_plot.getAxis('bottom').setLabel('AI0')


        #self._app.aboutToQuit.connect(self.stop)
        self._app.setQuitOnLastWindowClosed(False)
        self._app.lastWindowClosed.connect(self.__del__)



        # Axis xlimits
        ##set(self.hAxes, 'XLim', [0,length(self.waveform)/self.sample_rate*1E3], 'Box', 'on')
        ##grid on

        # Legend
        #legend('command','galvo position')


        # Start of code for making the blue inset plot
        ##self.hAxesXY = axes('Parent', self.hFig, 'Position', [0.8,0.1,0.2,0.2], 'NextPlot', 'add')
        ##self.hPltDataXY = plot(self.hAxesXY, zeros(100,1), '-b.')
        ##set(self.hAxesXY, 'XTickLabel', [], 'YTickLabel',[], \
        ##    'YLim',[-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15],'XLim',[-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15])

        #Add "crosshairs" to show x=0 and y=0
        ##plot(self.hAxesXY, [-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15], [0,0], ':k')
        ##plot(self.hAxesXY, [0,0], [-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15], ':k')

        ##self.hAxesXY.Color=[0.8,0.8,0.95,0.75]; #blue background  and transparent (4th input, an undocumented MATLAB feature)
        ##grid on
        ##box on
        ##axis square
        # End of code for making the inset plot


        self._win.show()

    def start(self):
        # This method starts acquisition on the AO then the AI task. 
        # Acquisition begins immediately since there are no external triggers.
        print('Starting tasks')
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

        #Report waveform properties
        if False:
            print(np.size(self.waveform))
            print(self.waveform)
            import matplotlib.pyplot as plt 
            plt.plot(self.waveform)
            plt.show()
        print('Generated a waveform of length %d and a line period of %0.3f ms (%0.1f Hz)' % \
               (self.pixels_per_line, self.line_period()*1E3, 1/self.line_period()))
    #close generate_scan_waveform


    def read_and_display_data(self,tTask, event_type, num_samples, callback_data):
        # This callback method is run each time data have been acquired.
        data = self.ai_task.read(number_of_samples_per_channel=len(self.waveform))

        ## Updating the window title too often seems to lock the GUI on Win10
        #self._win.setWindowTitle('Plot update #%d' % self._read_number)
        self._read_number += 1
        #print("Callback %d" % self._read_number)


        self._plt_ao0.setData(data[0])
        self._plt_ai0.setData(data[1])
        self._plt_phase.setData(data[0],data[1])


        # Read data off the DAQ
        #inData = readAnalogData(src,src.everyNSamples,'Scaled')

        #timeAxis = np.arange(0,len(inData)-1) / self.sample_rate*1E3;
        #self.hPltDataAO0.YData = inData[:,1]
        #self.hPltDataAO0.XData=timeAxis
        #Scale the feedback signal so it's the same amplitude as the command
        #scaleFactor = max(inData[:,1]) / max(inData[:,2])
        #self.hPltDataAO1.YData = inData[:,2]*scaleFactor
        #self.hPltDataAO1.XData=timeAxis;

        #self.hPltDataXY.YData = inData[:,2]*scaleFactor
        #self.hPltDataXY.XData = inData[:,1]

        return 0
    #close read_and_display_data


    def line_period(self):
        if len(self.waveform)==0:
            LP=[]
        else:
            LP = len(self.waveform) / (self.sample_rate*self.num_reps_per_acq)

        return LP
    # close line_period



if __name__ == '__main__':
    W=waveformTester()
    input('Press return to stop\n')
