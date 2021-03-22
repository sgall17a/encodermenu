
import math
from machine import Pin, I2C
import ssd1306
import sys
import time
from neopixel import *
import neopixel
import uasyncio as asyncio

#from guimenu importMenu
#import _thread

from rotary_irq_pico  import RotaryIRQ
#import uasyncio as asyncio

switch = Pin(18,Pin.IN,Pin.PULL_DOWN)
i2c = I2C(0, scl=Pin(17), sda=Pin(16))

led = Pin(25,Pin.OUT)

oled = ssd1306.SSD1306_I2C(128, 64, i2c)

encoder = RotaryIRQ(pin_num_clk=12, 
              pin_num_dt=13, 
              min_val=0, 
              max_val=100, 
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_WRAP,
              pull_up=True)

#  Hardware abstraction


def display(text1,text2):
    oled.fill(0)
    oled.text(text1,0,0)
    oled.text(text2,0,30)
    oled.show()

sethours   = wrap_object( GetInteger(low_v=1,high_v=24,increment=1,caption='Hours',field='hour'))
setminutes = wrap_object( GetInteger(low_v=0,high_v=59,increment=1,caption='Minute',field='minute'))
setseconds = wrap_object( GetInteger(low_v=0,high_v=59,increment=1,caption='Second',field='second'))

setyears   = wrap_object( GetInteger(low_v=1,high_v=24,increment=1,caption='Year',field='year'))
setdays    = wrap_object( GetInteger(low_v=1,high_v=31,increment=1,caption='Day',field='day'))
setmonths  = wrap_object( GetInteger(low_v=1,high_v=12,increment=1,caption='Month',field='month'))

showdatetime = wrap_object(Info('Current Datetime\nThis datetime'))
setclock   = wrap_object( Info('Set up\nTHE CLOCK\nOK'))

opendoor= info('Open door\n---------')
closedoor= info('Close door\n.............')
automate= info('Automate door\n#################')

#asyncio.run(blue(3))
print('finished')

    
num_pixels = 75
   
#just an example of using the get_integer method.
brightness = wrap_object(GetInteger(low_v=0,high_v=10,increment=10,caption='Brightness(%)',field='brightness'))


def hue(h,l=0.4,s=0.999):
    r,g,b = [int(256* a) for a in colorsys.hls_to_rgb(h, l, s)]
    return "#%02x%02x%02x"%(r,g,b)  
    
def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)
    
def ablue():
    "Menu function One way to call an async function"
    stop()
    async def temp():
        neopixel.pixels_fill(BLUE)
        pixels_show()
    make_task(temp)

def showcolour():
    "Menu function.  Ignores self and makes neopixels blue"
    print('data',data.get('color1','RED'))
    stop()
    async def dummy():
        coltup = eval('neopixel.'+data.get('colour1','GREEN'))
        neopixel.pixels_fill(coltup)
        pixels_show()
    make_task(dummy)
        
  
def red():
    print ('red')
    stop()   
    async def temp():
        pixels_fill(RED)
        pixels_show()
    make_task(temp)
        
def rainbow():
    "call an async function defined elsewhere"
    print('start rainbow')
    stop()
    make_task(rainbow_cycle)


async def rainbow_cycle():
    "Show a rainbow but yield frequently for menus etc"
    for k in range(255):
        for j in range(255):
            for i in range(NUM_LEDS):
                rc_index = (i * 256 // NUM_LEDS) + j
                neopixel.pixels_set(i, wheel(rc_index & 255))
                await asyncio.sleep(0)
            neopixel.pixels_show()
            await asyncio.sleep(0)

def yellow():
    stop()
    async def dummy():
        neopixel.pixels_fill(YELLOW)
        neopixel.pixels_show()
    make_task(dummy)

trees     = wrap_menu( [('gum',data),('tea-tree',data),('red-gum count',data),('willow',data),('Back!',back)])
patterns  = wrap_menu( [('Chaser',yellow),('Show colour',showcolour),('Blue',ablue),('Rainbow',rainbow),('Back!',back)])
main_menu = wrap_menu( [('Patterns',patterns),('trees',trees),('Brightness',brightness)])

colour1 = selection('colour1',['RED',('Green','GREEN'),('Blue','BLUE'),('Yellow','YELLOW'),('WHITE','white')])

timewizard = wizard([("Hours",sethours),("Minutes",setminutes),("Seconds",setseconds)])
datewizard = wizard([('Years',setyears),("Months",setmonths),("Days",setdays)])
pixels = wrap_menu([('Show color',showcolour)])
settime = wrap_menu( [('Time wizard',timewizard),('Date wizard',datewizard),('Write to clock',setclock),('Show datetime',showdatetime),("Back..",back)])
                
root_menu = wrap_menu([('Set DateTime',settime),('Colour 1',colour1),('Patterns',patterns),('Open door',opendoor),('Close door',closedoor),('Automate door',automate)])

root_menu()

run_async(mainloop)

