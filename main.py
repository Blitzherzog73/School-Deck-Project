from machine import Pin, SoftSPI
from micropython import const
import time
import neopixel
import asyncio
import e_ink_display_driver_mpython
import framebuf

height = 200
width = 200 #it's actually 122 but changed to 128 to be a multiple of 8 | pixel 122 to 127 are dead pixels
real_width = const(200)
real_height = const(200)
renderbuf_black = bytearray((width // 8) * height)
#renderbuf_red = bytearray(width * height // 8)

#fbuf_red = framebuf.FrameBuffer(renderbuf_red , width, height, framebuf.MONO_HLSB)
fbuf_black = framebuf.FrameBuffer(renderbuf_black, width, height, framebuf.MONO_HLSB)

white = const(1)
black = const(0)
#red = const(0)

din = Pin(19, Pin.OUT) #before 9 now 19
clk = Pin(18, Pin.OUT)
cs = Pin(11, Pin.OUT)
dc = Pin(10, Pin.OUT)
rst = Pin(1, Pin.OUT)
busy = Pin(0, Pin.IN)
spi = SoftSPI(baudrate=1000000, polarity=0, phase=0, sck=clk, mosi=din, miso=Pin(2)) #Pin 2 is an unsused pin

epaper_display = e_ink_display_driver_mpython.EPD(spi=spi, cs=cs, dc=dc, rst=rst, busy=busy)

led = Pin(8, Pin.OUT)
debug_led = neopixel.NeoPixel(led, 1)

def start_program():
    debug_led[0] = (0, 0, 255)
    debug_led.write()
    time.sleep(0.5)
    debug_led[0] = (0,0,0)
    debug_led.write()
    
'''
def clear_display():
    epaper_display.draw_filled_rectangle(buf, 0, 0, real_width - 1, real_height - 1, white)
    epaper_display.display_frame(buf, buf)
    #epaper_display.draw_filled_rectangle(buf, 0, 0, real_width - 1, real_height - 1, white)
'''
def test():
    print("start test")
    time.sleep(2)
    color = white
    x1 = 40
    x2 = 119
    y1 = 119
    y2 = 40
    '''
    for i in range(3):
        print("starting round: " + str(i))
        c = ""
        if color == black:
            c = "black"
        elif color == white:
            c = "white"
        print("display colour: " + c)
        '''
    '''
    if color == black:
        color = white
    elif color == white:
        color = black
    '''
    #fbuf_red.fill(white)
    epaper_display.init()
    #epaper_display.reset_display_size()
    #epaper_display.set_partial_refresh(x1, y1, x2, y2)
    #partial_buffer = bytearray((x2 - x1 + 1) * (y1 - y2 + 1)//8)
    #print("partial buffer: " + str(partial_buffer))
    #partial_framebuffer = framebuf.FrameBuffer(partial_buffer, 200, 100, framebuf.MONO_HLSB)
    
    #partial_framebuffer.fill(black)
    #epaper_display.fill(white)
    #epaper_display.line(black, 0, 0, 150, 100)
    #epaper_display.line(black, 0, 0, 0, 4)
    #epaper_display.line(black, 7, 0, 7, 199)
    #epaper_display.line(black, 75, 10, 199, 60)
    #epaper_display.line(black, 50, 0, 50, 199)
    #epaper_display.line(black, 100, 0, 100, 199)
    #fbuf_black.fill(white)
    #epaper_display.set_image(renderbuf_black)
    epaper_display.set_image()
    
    epaper_display.image_update()
    epaper_display.deep_sleep()
    print("after deep sleep")
    time.sleep(15)
    print("15 sec tick")
    #epaper_display.sleep()
    #clear_display()
    #fbuf_black.fill(white)
    #epaper_display.display_frame(buf, buf)
    #fbuf_black.fill(black)
    '''for i in range(0, real_height - 1, 2):
        if i < real_height:
            fbuf_black.hline(0, i, i + 1, black)
    for i in range(1, real_height - 1, 2):
            if i < real_height:
                fbuf_red.hline(0, i, i + 2, red)'''
    #epaper_display.display_frame(buf, buf)
    #epaper_display.sleep()
    print("finish")
    
start_program()
test()