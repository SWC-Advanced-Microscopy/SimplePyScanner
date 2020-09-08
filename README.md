# SimplePyScanner

Simple Python 2-photon scanning software for demo and teaching purposes.

## What is this?

A 2-photon microscope is a laser-scanning microscope that builds up an image by sweeping a laser beam across a specimen in a [raster pattern](https://en.wikipedia.org/wiki/Raster_scan). The laser excites fluorescent proteins which emit light of a different wavelength to that with which they were excited. 
This emitted light is detected using one or more [PMTs](https://en.wikipedia.org/wiki/Photomultiplier). 
Emitted light and excitation light are of different wavelengths and so can be isolated with [dichroic mirrors](https://en.wikipedia.org/wiki/Dichroic_filter) and optical
band-pass filters. 
Similarly, emitted light of different wavelengths (e.g. from different fluorescent molecules) can be split by dichroic mirrors and detected at different PMTs. 

The 2-photon microscope takes its name from the [2-photon effect](https://en.wikipedia.org/wiki/Two-photon_excitation_microscopy) that is used to excite the fluorophores in the specimen. 
Here, single fluorophore molecules emit a short-wave photon after being excited by two long-wave photons that are absorbed simultaneously. 
This is the opposite of what typically occurs in fluorescence (one shorter wave photon excites a molecule to release one longer wave photon). 
The 2-photon effect is made possible by high frequency pulsed lasers, where the peak power is many thousands of times higher than the mean power. 
For example, the [Mai Tai laser](http://www.spectra-physics.com/products/ultrafast-lasers/mai-tai#specs) from Spectraphysics has a mean power of about 2 W but a peak power of about 500 kW. 

One interesting feature of 2-photon microscopes is that they are [relatively easy to build](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0110475) with off the shelf parts. 
In order to acquire an image, the beam needs to be scanned across the specimen and the emitted light collected. 
This repository contains simple code that orchestrates this process. 
**SimplePyScanner** is a collection of example tutorial code to show how to write scanning software for a linear scanning (not resonant) 2-photon microscope. 
SimpleMScanner is a teaching aid, not a complete application.


## What you will need
You should first be familiar with NI DAQmx in Python. 
For more details see [the TENSS Python DAQmx examples](https://github.com/tenss/Python_DAQmx_examples).
You will also need an NI device to coordinate scanning and data acquisition. 
The present code been tested on NI USB-6361 devices but should work on a range of hardware.
Of course you will also need at least a set of scan mirrors, a scan lens, a tube lens, an objective, some form of detector and a laser. 
For educational purposes, it is possible to use a laser pointer and a photo-diode that detects transmitted light through a thin, high contrast, sample such as an EM grid. 


## Dependencies
This code requires the `numpy`, `matplotlib`, and `pyqtgraph`. 
You will also need to install [DAQmx](https://www.ni.com/en-gb/support/downloads/drivers/download.ni-daqmx.html). 
The latest version should be fine.
If you are not already familiar with `pyqtgraph` it's worth trying:

```
import pyqtgraph.examples
pyqtgraph.examples.run()
```

# Also see
* For basic DAQmx examples and other introductory concepts see [Python_DAQmx_examples](https://github.com/tenss/Python_DAQmx_examples)
* [SimpleMScanner]https://github.com/tenss/SimpleMScanner)
* [HelioScan](http://helioscan.github.io/HelioScan/)
* [SciScan](http://www.scientifica.uk.com/products/scientifica-sciscan)
* [ScanImage](https://vidriotechnologies.com/)
* [LSMAQ](https://github.com/danionella/lsmaq) - which is a very similar project but written in MATLAB

# Disclaimer
This software is supplied "as is" and the author(s) are not responsible for hardware damage, blindness, etc, caused by use (or misuse) of this software. 
High powered lasers should only be operated by trained individuals. 
It is good practice to confirm the scan waveforms with an oscilloscope before feeding them to the scan mirrors. 
Start with smaller amplitude scan patterns and lower frame rates so as not to damage your scanners. 
Immediately stop scanning if the mirrors make unusual chirping noises and/or the image breaks down.
PMTs can be damaged by normal ambient light levels and must be operated in the dark.