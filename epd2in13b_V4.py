# *****************************************************************************
# * | File        :	  epd2in13b_V4.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2022-04-21
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

#import logging
from micropython import const

# Display resolution
EPD_WIDTH       = 122
EPD_HEIGHT      = 250


'''command list'''
SET_RAM_X_ADDRESS_START_END_POSITION = const(0x44)
SET_RAM_Y_ADDRESS_START_END_POSITION = const(0x45)
SET_RAM_X_ADDRESS_COUNTER = const(0x4E)
SET_RAM_Y_ADDRESS_COUNTER = const(0x4F)

SWRESET = const(0x12)
DRIVER_OUTPUT_CONTROL = const(0x01)
DATA_ENTRY_MODE = const(0x11)
BORDER_WAVE_FROM = const(0x3C)
READ_BUILT_IN_TEMPERATURE_SENSOR = const(0x18)
DISPLAY_UPDATE_CONTROL = const(0x21)
TURN_ON_DISPLAY = const(0x20)
WRITE_RAM_BLACK_WHITE = const(0x24)
WRITE_RAM_RED_WHITE = const(0x26)
DEEP_SLEEP = const(0x10)
CHECK_CODE = const(0x01)



#logger = logging.getLogger(__name__)
from time import sleep_ms

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.reset_pin = rst
        self.dc_pin = dc
        self.busy_pin = busy
        self.cs_pin = cs
        self.spi = spi
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    # hardware reset
    def reset(self):
        self.reset_pin(1)
        sleep_ms(20) 
        self.reset_pin(0)
        sleep_ms(2)
        self.reset_pin(1)
        sleep_ms(20)   

    # send 1 byte command
    def send_command(self, command):
        self.dc_pin(0)
        self.cs_pin(0)
        self.spi.write(bytearray([command]))
        self.cs_pin(1)
    
    # send 1 byte data
    def send_data(self, data):
        self.dc_pin(1)
        self.cs_pin(0)
        self.spi.write(bytearray([data]))
        self.cs_pin(1)
        
    # send a lot of data   
    def send_data2(self, data):
        self.dc_pin(1)
        self.cs_pin(0)
        self.spi.write(data)
        self.cs_pin(1)
        
    # judge e-Paper whether is busy
    def busy(self):
        #logger.debug("e-Paper busy")
        while(self.busy_pin.value() != 0): 
            sleep_ms(10)
        #logger.debug("e-Paper busy release")

    # set the display window
    def set_windows(self, xstart, ystart, xend, yend):
        self.send_command(SET_RAM_X_ADDRESS_START_END_POSITION)
        self.send_data((xstart>>3) & 0xff)
        self.send_data((xend>>3) & 0xff)
        
        self.send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self.send_data(ystart & 0xff)
        self.send_data((ystart >> 8) & 0xff)
        self.send_data(yend & 0xff)
        self.send_data((yend >> 8) & 0xff)
        
    # set the display cursor(origin)
    def set_cursor(self, xstart, ystart):
        self.send_command(SET_RAM_X_ADDRESS_COUNTER)
        self.send_data(xstart & 0xff)

        self.send_command(SET_RAM_Y_ADDRESS_COUNTER)
        self.send_data(ystart & 0xff)
        self.send_data((ystart >> 8) & 0xff)

    # initialize 
    def init(self):
            
        self.reset()

        self.busy()
        self.send_command(SWRESET)
        self.busy()   

        self.send_command(DRIVER_OUTPUT_CONTROL)   
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(DATA_ENTRY_MODE) # data entry mode       
        self.send_data(0x03) #0x01

        self.set_windows(0, 0, self.width - 1, self.height - 1)
        self.set_cursor(0, 0)

        self.send_command(BORDER_WAVE_FROM) # BorderWavefrom
        self.send_data(0x05)	

        self.send_command(READ_BUILT_IN_TEMPERATURE_SENSOR) # Read built-in temperature sensor
        self.send_data(0x80)	

        self.send_command(DISPLAY_UPDATE_CONTROL) # Display update control
        self.send_data(0x80)	
        self.send_data(0x80)

        self.busy()
        
        return 0

    # turn on display
    def ondisplay(self):
        self.send_command(TURN_ON_DISPLAY)
        self.busy()

    # image converted to bytearray
    def getbuffer(self, image):
        img = image
        imwidth, imheight = img.size
        if(imwidth == self.width and imheight == self.height):
            img = img.convert('1')
        elif(imwidth == self.height and imheight == self.width):
            # image has correct dimensions, but needs to be rotated
            img = img.rotate(90, expand=True).convert('1')
        else:
            #logger.warning("Wrong image dimensions: must be " + str(self.width) + "x" + str(self.height))
            # return a blank buffer
            return [0x00] * (int(self.width/8) * self.height)

        buf = bytearray(img.tobytes('raw'))
        return buf

    # display image
    def display(self, imageblack, imagered):
        self.send_command(WRITE_RAM_BLACK_WHITE)
        self.send_data2(imageblack)
        
        self.send_command(WRITE_RAM_RED_WHITE)
        self.send_data2(imagered)
        
        self.ondisplay()
        
    # display white image
    def clear(self):
        if self.width%8 == 0:
            linewidth = int(self.width/8)
        else:
            linewidth = int(self.width/8) + 1
            
        buf = [0xff] * (int(linewidth * self.height))
            
        self.send_command(WRITE_RAM_BLACK_WHITE)
        self.send_data2(bytearray(buf))
        
        self.send_command(WRITE_RAM_RED_WHITE)
        self.send_data2(bytearray(buf))
        
        self.ondisplay()

    # Compatible with older version functions
    def Clear(self):
        self.clear()

    # sleep
    def sleep(self):
        self.send_command(DEEP_SLEEP)
        self.send_data(CHECK_CODE)
        
        sleep_ms(2000)
        '''module_exit()'''
### END OF FILE ###

