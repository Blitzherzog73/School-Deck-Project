from machine import Pin, SoftSPI
from micropython import const
import time
import asyncio
import e_ink_display_driver_mpython

din = Pin(19, Pin.OUT) #before 9 now 19
clk = Pin(18, Pin.OUT)
cs = Pin(11, Pin.OUT)
dc = Pin(10, Pin.OUT)
rst = Pin(1, Pin.OUT)
busy = Pin(0, Pin.IN)
spi = SoftSPI(baudrate=1000000, polarity=0, phase=0, sck=clk, mosi=din, miso=Pin(2)) #Pin 2 is an unsused pin

epaper_display = e_ink_display_driver_mpython.EPD(spi=spi, cs=cs, dc=dc, rst=rst, busy=busy)

display_width = const(200)
display_height = const(200)

grid = None

class Point():
    x = None
    y = None
    def __init__(self, x1 = None, y1 = None):
        self.x = x1
        self.y = y1

class Grid():
    def __init__(self, rows, columns, top_left_point = Point(0, 0), bottom_right_point = Point(display_width - 1, display_height - 1), display = epaper_display):
        self.display = display
        self.grid_left_x = top_left_point.x
        self.grid_right_x = bottom_right_point.x
        self.grid_up_y = top_left_point.y
        self.grid_bottom_y = bottom_right_point.y
        self.amount_rows = rows
        self.amount_columns = columns
        
        
    async def draw_grid(self):
        print("hi from draw grid")
        internal_grid_lines_rows = self.amount_rows - 1
        internal_grid_lines_columns = self.amount_columns - 1
        grid_width = self.grid_right_x - self.grid_left_x + 1
        grid_height = self.grid_bottom_y - self.grid_up_y + 1
        column_width = grid_width // self.amount_columns
        row_height = grid_height // self.amount_rows
        
        if internal_grid_lines_columns > 0:
            for column_grid_line in range(internal_grid_lines_columns):
                new_column_x = self.grid_left_x + (column_grid_line + 1) * column_width - 1
                self.draw_grid_lines_column(new_column_x)
        if internal_grid_lines_rows > 0:
            for row_grid_line in range(internal_grid_lines_rows):
                new_grid_y = self.grid_up_y + (row_grid_line + 1) * row_height - 1
                self.draw_grid_lines_row(new_grid_y)
            
            
        self.display.display_image()
        self.display.deep_sleep()
    
    
    
    def draw_grid_lines_row(self, y):
        self.display.line(self.grid_right_x, y, self.grid_left_x, y)
    
    def draw_grid_lines_column(self, x):
        self.display.line(x, self.grid_up_y, x, self.grid_bottom_y)
        

async def set_up(grid_rows, grid_columns):
    global grid
    grid = Grid(grid_rows, grid_columns)
    asyncio.create_task(grid.draw_grid())
    await asyncio.sleep(2)