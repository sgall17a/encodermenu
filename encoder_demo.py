"""
Demo for the encoder_menu library

This library is for  simple but powerful and intuitive menus
on MCUs running Micropython.

The idea is that various functions can started (or stopped) from a menu.
The example uses some neopixel patterns.

There is also  data entry capacity, integer and strings.

The hardware requirements are basic: a display, a rotary encoder and a switch or button.

"""

from encoder_menu import *
#Good practive says we should import each function but it is a bit verbose
#from encoder_menu import get_integer,info,selection,wizard,wrap_menu,menu_data,dummy,back,run_menu,set_data


# Neopixels are used as an example.
# In real life your  functions would go in their own different module
from neopixel import *

# ORDER MATTERS!!
#We have to define things before they can be  used

#Define our default data values first




set_data('hour',12)
set_data('minute',30)
set_data('second',27)
set_data('colour1','GREEN')
set_data('speed',5)
#print (menu_data)

# Now define out data entry and info functions and other action related functions.
#In this example the action functions relate to neopixels.
#and these functions have been declared in their own module for clarity

#define some "get_integer functions for inputing numerical values
#The first example shows the name and order of parameters.
sethours   = get_integer(low_v=1,high_v=24,increment=1,caption='Hours',field='hour')
#Now that we know the order we dont have to repeat the names
setminutes = get_integer( 0, 59 , 1, 'Minute','minute')
setseconds = get_integer(0,59,1,'Second','second')
setyears   = get_integer(1,24,1,'Year','year')
setdays    = get_integer(1,31,1,'Day','day')
setmonths  = get_integer(1,12,1,'Month','month')
brightness = get_integer(0,10,10,'Brightness(%)','brightness')
speed = get_integer(0,20,5,'Speed (0-100)','speed')
hue = get_integer(0,100,1,'Hue (0-100)','hue')

#define some info functions for showing help or status information

colors = ['RED',('Green','GREEN'),'BLUE','YELLOW','ORANGE','PURPLE','WHITE','BLACK']

datetimeinfo = info('Current Datetime\nThis datetime')
setclockinfo   = info('Set up\nTHE CLOCK\nOK')
opendoor= info('Open door\n---------')
closedoor= info('Close door\n.............')
automate= info('Automate door\n#################')

#define a selection

colour1 = selection('colour1',colors)
colour2 = selection('colour2',colors)

# Now that we have our entry functions we can define some wizards

timewizard = wizard([("Hours",sethours),("Minutes",setminutes),("Seconds",setseconds)])
datewizard = wizard([('Years',setyears),("Months",setmonths),("Days",setdays)])

# Now  we have all our action functions  we can define the menus and submenus
# The actual neopixel related functions have been put in the neopixel module


trees     = wrap_menu( [('gum',dummy),('tea-tree',dummy),('red-gum count',dummy),('willow',dummy),('Back!',back)])
patterns  = wrap_menu( [('Chaser',yellow),('Show colour',showcolour),('Blue',ablue),('Rainbow',rainbow),('Back!',back)])
main_menu = wrap_menu( [('Patterns',patterns),('trees',trees),('Brightness',brightness)])
pixels = wrap_menu([('Show color',showcolour)])
settime = wrap_menu( [('Time wizard',timewizard),('Date wizard',datewizard),('Write to clock',setclockinfo),
                      ('Show datetime',datetimeinfo),("Back..",back)])

settings = wrap_menu([('Colour1',colour1),('Colour2',colour2),('Brightness',brightness),('Hue',dummy),('Speed',speed),('Saturation',dummy)])
 
#Root menu should be last menu because it depends on all the previous things
root_menu = wrap_menu([('Set DateTime',settime),('Colour 1',colour1),('Speed',speed),('Patterns',patterns),('Open door',opendoor),
                       ('Close door',closedoor),('Automate door',automate)])

#Finally we set up the root menu and set it running

root_menu()  # Set up the initial root menu by calling its function
run_menu() #Start the main loop running


print('finished -  This should never get here because menu is an endless loop') 




