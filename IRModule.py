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

class IRRemote:    

    def __init__(self, callback = None):        

        self.decoding = False
        self.pList = []
        self.timer = time.time()
        if callback == 'DECODE':
            self.callback = self.print_ir_code
        else:
            self.callback = callback
        self.checkTime = 150  # time in milliseconds
        self.verbose = False
        self.repeatCodeOn = True
        self.lastIRCode = 0
        self.maxPulseListLength = 70

    def pWidth(self, pin):
        """pWidth, function to record the width of the highs and lows
        of the IR remote signal and start the function to look for the
        end of the IR remote signal"""

        self.pList.append(time.time()-self.timer)
        self.timer = time.time()        

        if self.decoding == False:
            self.decoding = True
            check_loop = threading.Thread(name='self.pulse_checker',target=self.pulse_checker)
            check_loop.start()           
            
        return

    def pulse_checker(self):
        """pulse_checker, function to look for the end of the IR remote
        signal and activate the signal decode function followed by
        the callback function.

        End of signal is determined by 1 of 2 ways
        1 - if the length of the pulse list is larger than self.maxPulseListLength
          - used for initial button press codes
        2 - if the length of time receiving the pulse is great than self.checkTime
          - used for repeat codes"""

        timer = time.time()

        while True:                
                check = (time.time()-timer)*1000
                if check > self.checkTime:                    
                    print(check, len(self.pList))
                    break
                if len(self.pList) > self.maxPulseListLength:
                    print(check, len(self.pList))
                    break
                time.sleep(0.001)

        if len(self.pList) > self.maxPulseListLength:
            decode = self.decode_pulse(self.pList)
            self.lastIRCode = decode

        # if the length of self.pList is less than 10
        # assume repeat code found
        elif len(self.pList) < 10:
            if self.repeatCodeOn == True:
                decode = self.lastIRCode
            else:
                decode = 0
                self.lastIRCode = decode
        else:
            decode = 0
            self.lastIRCode = decode

        self.pList = []
        self.decoding = False

        if self.callback != None:
            self.callback(decode)
        
        return

    def decode_pulse(self,pList):
        """decode_pulse,  function to decode the high and low
        timespans captured by the pWidth function into a binary
        number"""

        bitList = []
        sIndex = -1

        # convert the timespans in seconds to milli-seconds
        # look for the start of the IR remote signal
        
        for p in range(0,len(pList)):
            try:
                pList[p]=float(pList[p])*1000
                if self.verbose == True:
                    print(pList[p])
                if pList[p]<11:
                    if sIndex == -1:
                        sIndex = p
            except:            
                pass

        # if no acceptable start is found return -1

        if sIndex == -1:
            return -1

        if sIndex+1 >= len(pList):
            return -1
        
        #print(sIndex, pList[sIndex], pList[sIndex+1])

        if (pList[sIndex]<4 or pList[sIndex]>11):
            return -1

        if (pList[sIndex+1]<2 or pList[sIndex+1]>6):
            return -1

        """ pulses are made up of 2 parts, a fixed length low (approx 0.5-0.6ms)
        and a variable length high.  The length of the high determines whether or
        not a 0,1 or control pulse/bit is being sent.  Highes of length approx 0.5-0.6ms
        indicate a 0, and length of approx 1.6-1.7 ms indicate a 1"""    
        
           
        for i in range(sIndex+2,len(pList),2):
            if i+1 < len(pList):
                if pList[i+1]< 0.9:  
                    bitList.append(0)
                elif pList[i+1]< 2.5:
                    bitList.append(1)
                elif (pList[i+1]> 2.5 and pList[i+1]< 45):
                    #print('end of data found')
                    break
                else:
                    break

        if self.verbose == True:
            print(bitList)

        # convert the list of 1s and 0s into a
        # binary number

        pulse = 0
        bitShift = 0

        for b in bitList:            
            pulse = (pulse<<bitShift) + b
            bitShift = 1        

        return pulse

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

        print(hex(code))

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


    

    
                    
      
    
    
