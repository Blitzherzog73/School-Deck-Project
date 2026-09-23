
from micropython import const
import framebuf
from time import sleep_ms
import array

# Display resolution
EPD_WIDTH       = const(200)
EPD_HEIGHT      = const(200)


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

DISPLAY_UPDATE_CONTROL_TWO = const(0x22)

white = const(1)
black = const(0)

class Point():
    x = None
    y = None
    def __init__(self, x1 = None, y1 = None):
        self.x = x1
        self.y = y1

class EPD:
    upper_left_window_corner = None
    lower_right_window_corner = None
    
    def __init__(self, spi, cs, dc, rst, busy):
        self.reset_pin = rst
        self.dc_pin = dc
        self.busy_pin = busy
        self.cs_pin = cs
        self.spi = spi
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.renderbuf_black = bytearray(b'\xff' * (self.width // 8) * self.height)
        self.fbuf_black = framebuf.FrameBuffer(self.renderbuf_black, self.width, self.height, framebuf.MONO_HLSB)

    # hardware reset
    def reset(self):
        self.reset_pin(1)
        sleep_ms(20) 
        self.reset_pin(0)
        sleep_ms(2)
        self.reset_pin(1)
        sleep_ms(20)   
        
    def sw_reset(self):
        self.busy()
        print("swreset")
        self._send_command(SWRESET)
        self.busy()   

    def output_control(self):
        self._send_command(DRIVER_OUTPUT_CONTROL)   
        self._send_data(0xc7)
        self._send_data(0x00)
        self._send_data(0x00)
        
    def data_entry_mode(self):
        self._send_command(DATA_ENTRY_MODE)
        self._send_data(0x03)
    
    # send 1 byte command
    def _send_command(self, command):
        self.dc_pin(0)
        self.cs_pin(0)
        self.spi.write(bytearray([command]))
        self.cs_pin(1)
    
    # send 1 byte data
    def _send_data(self, data):
        self.dc_pin(1)
        self.cs_pin(0)
        self.spi.write(bytearray([data]))
        self.cs_pin(1)
        
    # send a lot of data   
    def _send_data2(self, data):
        self.dc_pin(1)
        self.cs_pin(0)
        self.spi.write(data)
        self.cs_pin(1)
        
    # judge e-Paper whether is busy
    def busy(self):
        #logger.debug("e-Paper busy")
        i = 0
        while(self.busy_pin.value() != 0):
            i = i + 1 
            sleep_ms(10)
        print("e-Paper busy release: " + str(i) + " rounds")


        
    def init(self):
        print("reset")
        self.reset()

        self.sw_reset() 

        print("output ctrl")
        self.output_control()

        #self._send_command(DATA_ENTRY_MODE) # data entry mode       
        #self._send_data(0x01) #0x01
        
        self.data_entry_mode()
        
        self.reset_display_size()
        
        
    
    def image_update(self):
        print("turn on display")
        self._send_command(TURN_ON_DISPLAY)
        self.busy()
        
    def set_image(self, buffer_black = None):
        print("send black data")
        if buffer_black != None:
            self._send_command(WRITE_RAM_BLACK_WHITE)
            self._send_data2(buffer_black)
        else:
            if self.lower_right_window_corner != None and self.upper_left_window_corner != None:
                new_area_data = self.calculate_area(self.upper_left_window_corner, self.lower_right_window_corner)
                x1 = self.upper_left_window_corner.x
                y1 = self.upper_left_window_corner.y
                x2 = self.lower_right_window_corner.x
                y2 = self.lower_right_window_corner.y
                if x1 == 0 and y1 == 0 and x2 == 199 and y2 == 199:
                    self._send_command(WRITE_RAM_BLACK_WHITE)
                    self._send_data2(self.renderbuf_black)
                    print("full refresh")
                else:
                    new_buffer = new_area_data[0]
                    new_width = new_area_data[1]
                    new_height = new_area_data[2]
                    print("width: " + str(new_width))
                    print("height: " + str(new_height))
                    #print("buffer: " + str(bytearray(((new_width+7)// 8) * new_height)))
                    new_framebuffer = framebuf.FrameBuffer(new_buffer, new_width, new_height, framebuf.MONO_HLSB)
                    print("x1: " + str(x1))
                    print("y1: " + str(y1))
                    new_framebuffer.blit(self.fbuf_black, -x1, -y1)
                    #print("blitted buffer: " + str(new_buffer))
                    self.set_partial_refresh(x1, y1, x2, y2)
                    self._send_command(WRITE_RAM_BLACK_WHITE)
                    self._send_data2(new_buffer)
                self.upper_left_window_corner = None
                self.lower_right_window_corner = None
                self.reset_display_size()
            else:
                self._send_command(WRITE_RAM_BLACK_WHITE)
                self._send_data2(self.renderbuf_black)
        
    def deep_sleep(self):
        self.busy()
        self._send_command(DEEP_SLEEP)
        self._send_data(0X01)
        
    def calculate_area(self, u_l_point, l_r_point):
        width = l_r_point.x - u_l_point.x + 1
        height = l_r_point.y - u_l_point.y + 1
        print("width: " + str(width))
        print("height: " + str(height))
        
        buffer = bytearray(((width + 7)// 8) * height)
        return [buffer, width, height]

        
    def update_window(self, x1 = None, x2 = None, y1 = None, y2 = None):
        if self.lower_right_window_corner == None and self.upper_left_window_corner == None:
            self.upper_left_window_corner = Point()
            self.lower_right_window_corner = Point()
            
            
            
            if x1 <= x2:
                self.upper_left_window_corner.x = x1
                self.lower_right_window_corner.x = x2
            elif x1 > x2:
                self.upper_left_window_corner.x = x2
                self.lower_right_window_corner.x = x1
            if y1 <= y2:
                self.upper_left_window_corner.y = y1 
                self.lower_right_window_corner.y = y2
            elif y2 < y1:
                self.upper_left_window_corner.y = y2
                self.lower_right_window_corner.y = y1
        else:
            old_left_x = self.upper_left_window_corner.x
            old_right_x = self.lower_right_window_corner.x
            old_upper_y = self.upper_left_window_corner.y
            old_lower_y = self.lower_right_window_corner.y
            self.upper_left_window_corner = None
            self.lower_right_window_corner = None
            self.upper_left_window_corner = Point()
            self.lower_right_window_corner = Point()
            left_x = None
            right_x = None
            upper_y = None
            bottom_y = None
            if x1 <= x2:
                left_x = x1
                right_x = x2
            elif x1 > x2:
                left_x = x2
                right_x = x1
            if y1 <= y2:
                upper_y = y1
                bottom_y = y2
            elif y1 > y2:
                upper_y = y2
                bottom_y = y1
            if old_left_x > left_x:
                self.upper_left_window_corner.x = left_x
            else:
                self.upper_left_window_corner.x = old_left_x
            if old_right_x < right_x:
                self.lower_right_window_corner.x = right_x
            else:
                self.lower_right_window_corner.x = old_right_x
            if old_upper_y > upper_y:
                self.upper_left_window_corner.y = upper_y
            else:
                self.upper_left_window_corner.y = old_upper_y
            if old_lower_y < bottom_y:
                self.lower_right_window_corner.y = bottom_y
            else:
                self.lower_right_window_corner.y = old_lower_y
                
        self.upper_left_window_corner.x = (self.upper_left_window_corner.x//8) * 8
        self.lower_right_window_corner.x = (((self.lower_right_window_corner.x + 1 + 7)//8) * 8) - 1
        print("upper left corner: " + str(self.upper_left_window_corner.x) + "|" + str(self.upper_left_window_corner.y))
        print("lower right corner: " + str(self.lower_right_window_corner.x) + "|" + str(self.lower_right_window_corner.y))
            
    
        
    def line(self, x1, y1, x2, y2, colour = black):
        print("line: " + str(x1) + "|" + str(y1) + " " + str(x2) + "|" + str(y2))
        #self.fbuf_black.fill(white)
        self.fbuf_black.line(x1, y1, x2, y2, colour)
        self.update_window(x1, x2, y1, y2)
        #self.set_image(self.renderbuf_black)
        
    def fill(self, colour):
        self.fbuf_black.fill(colour)
        self.update_window(0, self.width - 1, 0, self.height - 1)
        #self.update_window(0, )
        
    def rectangle(self, x, y, width, height, colour = black, fill = False):
        self.fbuf_black.rect(x, y, width, height, colour, fill)
        x1 = x
        x2 = x + width - 1
        y1 = y
        y2 = y + height - 1
        self.update_window(x1, x2, y1, y2)
        
    def circle(self, x , y, radius, colour = black, fill = False):
        self.fbuf_black.ellipse(x, y, radius, radius, colour, fill)
        x1 = x - radius + 1
        x2 = x + radius - 1
        y1 = y - radius
        y2 = y + radius 
        self.update_window(x1, x2, y1, y2)
        
    def ellipse(self, x , y, x_radius, y_radius, colour = black, fill = False):
        self.fbuf_black.ellipse(x, y, x_radius, y_radius, colour, fill)
        x1 = x - x_radius + 1
        x2 = x + x_radius - 1
        y1 = y - y_radius
        y2 = y + y_radius 
        self.update_window(x1, x2, y1, y2)
        
    def triangle(self, x0, y0, x1, y1, x2, y2, colour = black, fill = False):
        coords = array.array('h', [x0, y0, x1, y1, x2, y2])
        self.fbuf_black.poly(0, 0, coords, colour, fill)
        left_x = min(x0, x1, x2)
        right_x = max(x0, x1, x2)
        up_y = min(y0, y1, y2)
        bottom_y = max(y0, y1, y2)
        self.update_window(left_x, right_x, up_y, bottom_y)
        
    def text(self, text, x, y, colour = black):
        text_length = len(text)
        y1 = y
        y2 = y + 8 - 1
        x1 = x
        text_pixels = text_length * 8
        x2 = x + text_pixels - 1
        if x2 >= self.width:
            all_lines_of_text = self.split_text(x1, text)
            #print(all_lines_of_text)
            row_count = 0
            for row in all_lines_of_text:
                new_x2 = x1 + (len(row) * 8)
                new_y1 = y1 + (row_count * 8)
                new_y2 = new_y1 + 8 - 1
                print("row_index: " + str(row_count))
                print("x1: " + str(x1))
                print("new_x2: " + str(new_x2))
                print("new_y1: " + str(new_y1))
                print("new_y2: " + str(new_y2))
                print(row)
                self.fbuf_black.text(row, x1, new_y1, colour)
                self.update_window(x1, new_x2, new_y1, new_y2)
                row_count += 1
        else:
            self.fbuf_black.text(text, x, y, colour)
            self.update_window(x1, x2, y1, y2)
            
    def split_text(self, x1, text):
        print("split text start")
        characters_fit_in_row = (self.width - x1 - 1) // 8
        print("this is how many characters fit in one row: " + str(characters_fit_in_row))
        text_split = []
        current_character = 0
        new_row_text = ""
        for character in text:
            if characters_fit_in_row < current_character + 1:
                text_split.append(new_row_text)
                print("new list of strings:")
                print(text_split)
                new_row_text = ""
                current_character = 0
            new_row_text += character
            print("current character index: " + str(current_character))
            print("current string: " + new_row_text)
            current_character += 1
        print("last row text: " + new_row_text)
        text_split.append(new_row_text)
        print("last state of list of strings:")
        print(text_split)
        return text_split
        
    def set_partial_refresh(self, x1, y1, x2, y2):
        self._send_command(SET_RAM_X_ADDRESS_START_END_POSITION)
        self._send_data(x1//8)
        self._send_data(x2//8)
        self._send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self._send_data(y1)
        self._send_data(0x00)
        self._send_data(y2)
        self._send_data(0x00)
        self._send_command(SET_RAM_X_ADDRESS_COUNTER)
        self._send_data(x1//8)
        self._send_command(SET_RAM_Y_ADDRESS_COUNTER)
        self._send_data(y1)
        self._send_data(0x00)
        
        
    def reset_display_size(self):
        self._send_command(SET_RAM_X_ADDRESS_START_END_POSITION)
        self._send_data(0x00)
        self._send_data(0x18)
        self._send_command(SET_RAM_Y_ADDRESS_START_END_POSITION)
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0xC7)
        self._send_data(0x00)
        self._send_command(SET_RAM_X_ADDRESS_COUNTER)
        self._send_data(0x00)
        self._send_command(SET_RAM_Y_ADDRESS_COUNTER)
        self._send_data(0x00)
        self._send_data(0x00)
### END OF FILE ###

