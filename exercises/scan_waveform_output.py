'''
 Exercise in which a DAQ board will generate hardware-timed continuous analog output from two 
 channels without using a callback function

 scan_waveform_output

 Purpose
 You will do hardware-timed continuous analog output using sample regeneration instead of a callback function. 
 The buffer contents is played out repeatedly: once the end of the buffer is reached, the DAQ returns to the 
 beginning and resumes from there. 

 Monitoring the output
 If you lack an oscilloscope you may physically connect the analog output to 
 an analog input and monitor this using the NI MAX test panel. You likely will need
 to select RSE: http://www.ni.com/white-paper/3344/en/
 Ask MAX to display "AI0:1"
 
 Instructions
 - Wire AO0 to AO0 or to an osciloscope. Wire AO1 to AO1 or to an osciloscope. 
 - You will need to edit the lines at the locations marked by the string ### EDIT
 - There may be hints and instructions around those lines


 Run the code at the command line thus:
 python scan_waveform_output



 
For more:
https://github.com/tenss/Python_DAQmx_examples

'''

import nidaqmx
from nidaqmx.constants import (AcquisitionType,RegenerationMode)
import numpy as np

class scan_waveform_output():

    # Properties of the class defined here

    # Parameters for the acquisition (device and channels)
    dev_name = ''      ### EDIT  (The name of the DAQ device as shown in MAX)

    # Task configuration
    sample_rate = 5000       # Sample Rate in Hz
    galvo_amplitude =  5     # Scanner amplitude (defined as peak-to-peak/2)
    pixels_per_line =  256   # Number pixels per line for a sawtooth waveform (for sine wave this defines wavelength)


    x_waveform = []               # Vector containing the waveform for the x mirror (fast axis)
    y_waveform = []               # Vector containing the waveform for the y mirror (slow axis)

    daq_waveforms = []            # Will contain the x and y waveform data to be sent to the DAQ

    num_samples_per_channel = []  #The length of the waveform
    
    h_task = [] # DAQmx task handle


    def __init__(self, autoconnect=False):
        # This method is the constructor and runs once when the class is instantiated

        self.generate_waveforms()
        if autoconnect:
            self.create_task()
    #close constructor


    def generate_waveforms(self):
        ###EDIT -- complete this method
        self.y_waveform =   
        self.x_waveform = 

        # This must be a two column matrix. The first column is the waveform sent to AO0
        # and the second column is the waveform sent to AO1. 
        self.daq_waveforms = np.stack() ###EDIT
    #close generate_waveforms


    def create_task(self):
        # This method sets up an NI Task that will play out the waveforms

        # * Create a DAQmx task
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreatetask/
        self.h_task = nidaqmx.Task('scanwave')


        # * Set up analog output on channels 0 and 1
        #   C equivalent - DAQmxCreateAOVoltageChan
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcreateaovoltagechan/
        #   https://nidaqmx-python.readthedocs.io/en/latest/ao_channel_collection.html
        connect_at = '%s/ao0:1' % self.dev_name
        self.h_task.ao_channels.add_ao_voltage_chan(connect_at)


 
        # * Configure the sampling rate and the number of samples
        #   C equivalent - DAQmxCfgSampClkTiming
        #   http://zone.ni.com/reference/en-XX/help/370471AE-01/daqmxcfunc/daqmxcfgsampclktiming/
        #   https://nidaqmx-python.readthedocs.io/en/latest/timing.html
        self.num_samples_per_channel = len(self.waveform)  # The number of samples to be stored in the buffer per channel
        buffer_length = self.num_samples_per_channel*4 # TODO -- IS THIS NEEDED??
        self.h_task.timing.cfg_samp_clk_timing(rate = self.sample_rate, \
                                               samps_per_chan = buffer_length, \
                                               sample_mode = AcquisitionType.CONTINUOUS)


        # * Set up sample regeneration: i.e. the buffer contents will play continuously
        # http://zone.ni.com/reference/en-XX/help/370471AE-01/mxcprop/attr1453/
        # For more on DAQmx write properties: http://zone.ni.com/reference/en-XX/help/370469AG-01/daqmxprop/daqmxwrite/
        # For a discussion on regeneration mode in the context of analog output tasks see:
        # https://forums.ni.com/t5/Multifunction-DAQ/Continuous-write-analog-voltage-NI-cDAQ-9178-with-callbacks/td-p/4036271
        self.h_task.out_stream.regen_mode = RegenerationMode.ALLOW_REGENERATION
        print('Regeneration mode is set to: %s' % str(self.h_task.out_stream.regen_mode))



        # * Write the waveform to the buffer with a 2 second timeout in case it fails
        #   Writes doubles using DAQmxWriteAnalogF64
        #   http://zone.ni.com/reference/en-XX/help/370471AG-01/daqmxcfunc/daqmxwriteanalogf64/
        self.h_task.write(, timeout=2). ###EDIT
    #close create_task


#close class scan_waveform_output



if __name__ == '__main__':
    print('\nRunning demo for hardwareContinuousVoltageNoCallback_twoChannels\n\n')
    AO = hardwareContinuousVoltageNoCallback_twoChannels()
    AO.create_task()
    AO.h_task.start()
    input('press return to stop')
    AO.h_task.start()
