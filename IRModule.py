#!/usr/bin/env python3
"""IRModuleV2, module to use with IR sensor

created Apr 27, 2018 
modified - Apr 30, 2018
modified Apr 1, 2020 - added repeat code functionality"""

"""
Copyright 2018, 2019, 2020 Owain Martin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import RPi.GPIO as GPIO
import time, threading
from datetime import datetime 

class IRRemote:    

    def __init__(self, callback = None):        

        self.decoding = False
        if callback == 'DECODE':
            self.callback = self.print_ir_code
        else:
            self.callback = callback
        self.verbose = False
        #self.lastRecievedTime = None

    def pWidth(self, pin):
        """pWidth, function to record the width of the highs and lows
        of the IR remote signal and start the function to look for the
        end of the IR remote signal"""
        if self.decoding == False:
            self.decoding = True
            check_loop = threading.Thread(name='self.pulse_checker',target=self.getData)
            check_loop.start()           
            
        return

    def ConvertHex(self, BinVal): #Converts binary data to hexidecimal
        tmpB2 = int(str(BinVal), 2)
        return hex(tmpB2)
            
    def getData(self): #Pulls data from sensor
        PinIn = 17
        num1s = 0 #Number of consecutive 1s
        command = [] #Pulses and their timings
        binary = 1 #Decoded binary command
        previousValue = 0 #The previous pin state
        value = GPIO.input(PinIn) #Current pin state
        
        while value: #Waits until pin is pulled low
            value = GPIO.input(PinIn)
        
        startTime = datetime.now() #Sets start time

        while True:                
            if value != previousValue: #Waits until change in state occurs
                now = datetime.now() #Records the current time
                pulseLength = now - startTime #Calculate time in between pulses
                startTime = now #Resets the start time
                command.append((previousValue, pulseLength.microseconds)) #Adds pulse time to array (previous val acts as an alternating 1 / 0 to show whether time is the on time or off time)

        #Interrupts code if an extended high period is detected (End Of Command)	
        if value:
            num1s += 1
        else:
            num1s = 0

        if num1s > 10000:
            break
            
        #Reads values again
        previousValue = value
        value = GPIO.input(PinIn)
    
    #Covers data to binary
        for (typ, tme) in command:
            if typ == 1:
                if tme > 1000: #According to NEC protocol a gap of 1687.5 microseconds repesents a logical 1 so over 1000 should make a big enough distinction
                    binary = binary * 10 + 1
                else:
                    binary *= 10

        if len(str(binary)) > 34: #Sometimes the binary has two rouge charactes on the end
            binary = int(str(binary)[:34])
        #print("binary")
        #print(binary)
        command = self.ConvertHex(binary)
        #print("hex")
        #print(command)
        if self.callback != None:
            self.callback(command)
            #self.getData()
        time.sleep(0.01)    
        check_loop = threading.Thread(name='self.pulse_checker',target=self.getData)
        check_loop.start()
        return command

    def set_callback(self, callback = None):
        """set_callback, function to allow the user to set
        or change the callback function used at any time"""

        self.callback = callback

        return

    def remove_callback(self):
        """remove_callback, function to allow the user to remove
        the callback function used at any time"""

        self.callback = None

        return

    def print_ir_code(self, code):
        """print_ir_code, function to display IR code received"""

        #print(hex(code))
        print(code)

        return

    def set_verbose(self, verbose = True):
        """set_verbose, function to turn verbose mode
        on or off. Used to print out pulse width list
        and bit list"""

        self.verbose = verbose

        return

    def set_repeat(self, repeat = True):
        """set_repeat, function to enable and disable
        the IR repeat code functionality"""

        self.repeatCodeOn = repeat
        return

if __name__ == "__main__":

    def remote_callback(code):        

        # Codes listed below are for the
        # Sparkfun 9 button remote

        #print(hex(code))

        if code == 0x10EFD827:
            print("Power")
        elif code == 0x10EFF807:
            print('A')
        elif code == 0x10EF7887:
            print('B')
        elif code == 0x10EF58A7:
            print('C')
        elif code == 0x10EFA05F:
            print('Up Arrow')
        elif code == 0x10EF00FF:
            print('Down Arrow')
        elif code == 0x10EF10EF:
            print('Left Arrow')
        elif code == 0x10EF807F:
            print('Right Arrow')
        elif code == 0x10EF20DF:
            print('Select')
        else:
            print('.')  # unknown code

        return

    ir = IRRemote('DECODE')  
            
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # uses numbering outside circles
    GPIO.setup(16,GPIO.IN)   # set pin 16 to input
    GPIO.add_event_detect(16,GPIO.BOTH,callback=ir.pWidth)

    ir.set_verbose()
    print('Starting IR remote sensing using DECODE function')

    time.sleep(5)
    print('Setting up callback')
    ir.set_verbose(False)
    ir.set_callback(remote_callback)
    ir.set_repeat(True)

    try:

        while True:
            time.sleep(1)

    except:
        print('Removing callback and cleaning up GPIO')
        ir.remove_callback()
        GPIO.cleanup(16)


    

    
                    
      
    
    
