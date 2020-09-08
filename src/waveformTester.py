
'''
 Generate and test various galvo waveforms

 waveformTester


 Description:
 This is a tutorial class to explore the scan waveform. Parameters are set by editing the properties.


 Instructions
 * Hook up AO0 to the galvo command (input) voltage terminal.
 * Wire up the rack to copy AO0 to AI0
 * Connect AI1 to the galvo position (output) terminal.
 * Run: "S=waveformTester()" to connect to Dev1. If your device has a different ID
   you may run: "S=waveformTester('Dev3')" (or whatever is the ID of the device)

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


 Requirements
 DAQmx and the Vidrio dabs.ni.daqmx wrapper

 See Also:
 minimalScanner.py
'''

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
    hFig = []    # The handle to the figure which shows the data is stored here
    hAxes = []   # Handle for the main axes
    hAxesXY = [] # Handle fo the plot of AI1 as a function of AI0
    hPltDataAO0 = [] # AO0 plot data
    hPltDataAO1 = [] # AO1 plot data
    hPltDataXY = []  # AO0 vs AO1 plot data



    def __init(self,dev_name=''):

        # Optionally replace device name if needed
        if 'Dev' in dev_name:
            self.dev_name = dev_name

        # Call a method to connect to the DAQ. If the following line fails, the Tasks are
        # cleaned up gracefully and the object is deleted. This is all done by the method
        # call and by the destructor
        ##self.connect_to_daq()

        # Build the figure window
        #self.build_figure_window()


        # Start the acquisition
        ##self.start()
        print('Close figure to quit acquisition')


    def __del__(self):
        print('Running destructor')
        #if ~isempty(self.hFig) && isvalid(self.hFig)
        #    self.hFig.delete #Closes the plot window

        ##self.stop() # Call the method that stops the DAQmx tasks

        ##self.ai_task.close()
        ##self.ao_task.close()
    #close destructor


    def connect_to_daq(self):
        # Note how we try to name the methods in the most descriptive way possible
        # Attempt to connect to the DAQ and set it up. If we fail, we close the 
        # connection to the DAQ and tidy up
        try:
            # Create separate DAQmx tasks for the AI and AO
            self.ai_task = dabs.ni.daqmx.Task('signalReceiver')
            self.ao_task = dabs.ni.daqmx.Task('waveformMaker')

            #  Set up analog input and output voltage channels, digitizing over +/- 5V
            self.ai_task.createAIVoltageChan(self.dev_name, [0,1], [], -5, 5)
            self.ao_task.createAOVoltageChan(self.dev_name, 0)


            # * Set up the AI task

            # Configure the sampling rate and the number of samples so that we are reading back data at the end of each waveform
            self.generate_scan_waveform #This will populate the waveforms property

            self.ai_task.cfgSampClkTiming(self.sample_rate,'DAQmx_Val_ContSamps', size(self.waveform,1)*100 )

            # Call an anonymous function to read from the AI buffer and plot the images once per frame
            self.ai_task.registerEveryNSamplesEvent(self.read_and_display_data, size(self.waveform,1), false, 'Scaled')


            # * Set up the AO task
            # Set the size of the output buffer
            self.ao_task.cfgSampClkTiming(self.sample_rate, 'DAQmx_Val_ContSamps', size(self.waveform,1))

            # TODO -- just link the rates
            #if self.ao_task.sampClkRate != self.ai_task.sampClkRate:
            # TODO -- just link the rates
            #print(['WARNING: AI task sample clock rate does not match AO task sample clock rate. Scan lines will precess.\n', ...
            #       'This issue is corrected in polishedScanner, which uses a shared sample clock between AO and AI'])


            # Allow sample regeneration (buffer is circular)
            self.ao_task.set('writeRegenMode', 'DAQmx_Val_AllowRegen')

            # Write the waveform to the buffer with a 5 second timeout in case it fails
            self.ao_task.writeAnalogData(self.waveform, 5)

            # Configure the AO task to start as soon as the AI task starts
            self.ao_task.cfgDigEdgeStartTrig(['/',self.dev_name,'/ai/StartTrigger'], 'DAQmx_Val_Rising')
        except:
                #Tidy up if we fail
            self.delete
        # close connect_to_daq


    def build_figure_window(self):
        self.hFig = clf;
        ##set(self.hFig, 'CloseRequestFcn', @self.windowCloseFcn)

        #Make an empty axis and fill with blank data
        self.hAxes = axes('Parent', self.hFig, 'Position', [0.09,0.1,0.89,0.88], 'NextPlot', 'add', \
                'YLim',[-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15])
        self.hAxes.XLabel.String = 'Time (ms)';
        self.hAxes.YLabel.String = 'Voltage';
        self.hPltDataAO0 = plot(self.hAxes, zeros(100,1), '-k') # This plot object holds data from AO0
        self.hPltDataAO1 = plot(self.hAxes, zeros(100,1), '-r') # This plot object holds data from AO1


        set(self.hAxes, 'XLim', [0,length(self.waveform)/self.sample_rate*1E3], 'Box', 'on')
        ##grid on
        legend('command','galvo position')


        # Start of code for making the blue inset plot
        self.hAxesXY = axes('Parent', self.hFig, 'Position', [0.8,0.1,0.2,0.2], 'NextPlot', 'add')
        self.hPltDataXY = plot(self.hAxesXY, zeros(100,1), '-b.')
        set(self.hAxesXY, 'XTickLabel', [], 'YTickLabel',[], \
            'YLim',[-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15],'XLim',[-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15])

        #Add "crosshairs" to show x=0 and y=0
        plot(self.hAxesXY, [-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15], [0,0], ':k')
        plot(self.hAxesXY, [0,0], [-self.galvo_amplitude*1.15,self.galvo_amplitude*1.15], ':k')

        self.hAxesXY.Color=[0.8,0.8,0.95,0.75]; #blue background  and transparent (4th input, an undocumented MATLAB feature)
        ##grid on
        ##box on
        ##axis square
        # End of code for making the inset plot

        set(self.hFig,'Name', sprintf('Close figure to stop acquisition - waveform frequency=#0.1f HZ', 1/self.linePeriod) )



        def start(self):
            # This method starts acquisition on the AO then the AI task. 
            # Acquisition begins immediately since there are no external triggers.
            try:
                self.ao_task.start()
                self.ai_task.start()
            except:
                #Tidy up if we fail
                self.delete

        #close start


        def stop(self):
            # Stop the AI and then AO tasks
            print('Stopping the scanning AI and AO tasks')
            self.ai_task.stop;    # Calls DAQmxStopTask
            self.ao_task.stop;
        #close stop


        def generate_scan_waveform(self):
            # This method builds a simple ("unshaped") galvo waveform and stores it in the self.waveform

            if self.waveform_type == 'sawtooth':
                # The X waveform goes from +galvo_amplitude to -galvo_amplitude over the course of one line:
                xWaveform = linspace(-self.galvo_amplitude, self.galvo_amplitude, self.pixels_per_line) 

                # Repeat the X waveform a few times to ease visualisation on-screen
                xWaveform = repmat(xWaveform, 1, self.num_reps_per_acq)  # NOTE! It's a column vector [CHECK! TODO]
                
                self.waveform = xWaveform; # Assign to the waveform property which gets written to the DAQ

            elif self.waveform_type == 'sine':
                # sine wave
                self.waveform = self.galvo_amplitude *  sin(linspace(-pi*self.num_reps_per_acq, pi*self.num_reps_per_acq, self.pixels_per_line*self.num_reps_per_acq))

            #Report waveform properties
            print('Scanning with a waveform of length #d and a line period of #0.3f ms (#0.1f Hz)' % \
                  (self.pixels_per_line, self.linePeriod*1E3, 1/self.linePeriod))
        #close generate_scan_waveform


        def read_and_display_data(self,src,evnt):
            # This callback method is run each time data have been acquired.
            # This happens because the of the listener set up in the method connect_to_daq
            # on the "self.ai_task.registerEveryNSamplesEvent" line.

            # Read data off the DAQ
            inData = readAnalogData(src,src.everyNSamples,'Scaled')

            timeAxis = np.arange(0,len(inData)-1) / self.sample_rate*1E3;
            self.hPltDataAO0.YData = inData[:,1]
            self.hPltDataAO0.XData=timeAxis
            #Scale the feedback signal so it's the same amplitude as the command
            scaleFactor = max(inData[:,1]) / max(inData[:,2])
            self.hPltDataAO1.YData = inData[:,2]*scaleFactor
            self.hPltDataAO1.XData=timeAxis;

            self.hPltDataXY.YData = inData[:,2]*scaleFactor
            self.hPltDataXY.XData = inData[:,1]
        #close read_and_display_data



        def linePeriod(self):
            if len(self.waveform)==0:
               LP=[]
            else:
                LP = length(self.waveform) / (self.sample_rate*self.num_reps_per_acq)

            return LP
        # close linePeriod

