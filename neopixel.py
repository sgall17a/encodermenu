# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin
import rp2
import uasyncio as asyncio
from encoder_menu import stop, make_task,menu_data
import encoder_menu


# Configure the number of WS2812 LEDs.
NUM_LEDS = 13
PIN_NUM = 10
brightness = 0.2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)
    #print('I am here')

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)
 
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
 
#  
# async def rainbow_cycle():
#     wait =100
#     
#     for k in range(255):
#         print(k)
#         for j in range(255):
#             for i in range(NUM_LEDS):
#                 rc_index = (i * 256 // NUM_LEDS) + j
#                 pixels_set(i, wheel(rc_index & 255))
#                 await asyncio.sleep(0)
#             pixels_show()
#             await asyncio.sleep(0)
#             
# def sync_rainbow_cycle():
#     wait =100
# 
#     for j in range(255):
#         for i in range(NUM_LEDS):
#             rc_index = (i * 256 // NUM_LEDS) + j
#             pixels_set(i, wheel(rc_index & 255))
#         pixels_show()

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)


def rgb_to_hls(r, g, b):
    maxc = max(r, g, b)
    minc = min(r, g, b)
    sumc = (maxc+minc)
    rangec = (maxc-minc)
    l = sumc/2.0
    if minc == maxc:
        return 0.0, l, 0.0
    if l <= 0.5:
        s = rangec / sumc
    else:
        s = rangec / (2.0-sumc)
    rc = (maxc-r) / rangec
    gc = (maxc-g) / rangec
    bc = (maxc-b) / rangec
    if r == maxc:
        h = bc-gc
    elif g == maxc:
        h = 2.0+rc-bc
    else:
        h = 4.0+gc-rc
    h = (h/6.0) % 1.0
    return h, l, s



num_pixels = 75


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
        pixels_fill(BLUE)
        pixels_show()
    make_task(temp)

def showcolour():
    global menu_data
    "Menu function.  Ignores self and makes neopixels blue"
    print('menu_data',menu_data.get('colour1','RED'))
    stop()
    try:
        async def dummy():
            print('dummy menu_data',menu_data)
            s =  menu_data.get('colour1','GREEN')
            print('to be eval',s)
            coltup = eval(s)
            print('coltup',coltup)
            pixels_fill(coltup)
            pixels_show()
        make_task(dummy)
    except:
        pass
        
  
def red():
    print ('red')
    stop()   
    async def temp():
        pixels_fill(RED)
        pixels_show()
    make_task(temp)
        



async def rainbow_cycle():
    "Show a rainbow but yield frequently for menus etc"
    print('async raimnabo')
        for j in range(2):
            for i in range(NUM_LEDS):
                rc_index = (i * 256 // NUM_LEDS) + j*16
                pixels_set(i, wheel(rc_index & 255))
                #await asyncio.sleep(0)
                pixels_show()
            print(i,j)
            await asyncio.sleep_ms(50)

def rainbow():
    "call an async function defined elsewhere"
    print('start 333 rainbow')
    stop()
    make_task(rainbow_cycle)

def yellow():
    stop()
    async def dummy():
        pixels_fill(YELLOW)
        pixels_show()
    make_task(dummy)
    
    
    
#     

# print("fills")
# for color in COLORS:       
#     pixels_fill(color)
#     pixels_show()
#     time.sleep(0.2)
# 
# print("chases")
# for color in COLORS:       
#     color_chase(color, 0.01)
# 
# print("rainbow")
# rainbow_cycle(0)

