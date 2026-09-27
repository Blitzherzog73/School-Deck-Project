from machine import Pin, SoftSPI
from micropython import const
import time
import neopixel
import asyncio
import e_ink_display_driver_mpython
import school_deck_logic

height = 200
width = 200 
real_width = const(200)
real_height = const(200)


white = const(1)
black = const(0)

din = Pin(19, Pin.OUT)
clk = Pin(18, Pin.OUT)
cs = Pin(11, Pin.OUT)
dc = Pin(10, Pin.OUT)
rst = Pin(1, Pin.OUT)
busy = Pin(0, Pin.IN)
spi = SoftSPI(baudrate=1000000, polarity=0, phase=0, sck=clk, mosi=din, miso=Pin(2)) #Pin 2 is an unsused pin

epaper_display = e_ink_display_driver_mpython.EPD(spi=spi, cs=cs, dc=dc, rst=rst, busy=busy)

led = Pin(8, Pin.OUT)
debug_led = neopixel.NeoPixel(led, 1)

main_loop = asyncio.get_event_loop()

def start_program():
    debug_led[0] = (0, 0, 255)
    debug_led.write()
    time.sleep(0.5)
    debug_led[0] = (0,0,0)
    debug_led.write()
    



def test():
    print("start test")
    time.sleep(2)
    epaper_display.init()
    

    epaper_display.fill(white)
    #epaper_display.text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 0, 100, white)
    
    epaper_display.display_image()
    
    epaper_display.deep_sleep()
    print("after deep sleep")
    time.sleep(15)
    print("15 sec tick")
    
    print("finish")
    
    
    
start_program()
asyncio.run(school_deck_logic.set_up(11, 7))
#test()