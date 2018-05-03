# IR-Remote-Receiver-Python-Module
Python (2 or 3) module for receiving IR remote control signals (NEC format) on a Raspberry Pi 
using a TSOP382 IR Receiver

To use this module requires the RPi.GPIO module and you need to run your program as the root
 user,  i.e. sudo...

This module includes one example file. For my testing I used several remotes from around my 
house, the example file includes the codes for the Sparkfun 9 button remote.

The TSOP382 IR receiver has 3 legs which are connected as follows:
- 1 - PI GPIO - I used Pin 16
- 2 - Pi Gnd
- 3 - Pi 3.3V

To set up a IR object use:
- ir = IRModule.IRRemote(callback=yourfunctname)

To set up the Pi GPIO callback the following is required
- GPIO.setwarnings(False)
- GPIO.setmode(GPIO.BCM)      # uses numbering outside circles
- GPIO.setup(irPin,GPIO.IN)   # irPin = Pi pin connected to the output of the TSOP382 receiver
- GPIO.add_event_detect(irPin,GPIO.BOTH,callback=ir.pWidth)

To setup your program to provide the IR code being sent use the following
- ir.set_callback('DECODE')

To get a listing of the time spans of the IR pulse highs and lows use
- ir.set_verbose(True)

Current user functions include:
- set_callback(callback = yourfunctname)
- remove_callback()
- set_verbose(verbose = False)



Updated Apr 30, 2018
