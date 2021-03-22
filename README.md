# Micropython encoder based menu


This simple menu system  was developed  for  micropython,  a rotary encoder and a little 128 * 64 pixel OLED display.  It was developed  on a Raspberry Pi Pico but also runs on an ESP32 and ESP8266.

I used a little OLED but it could  adapted to other displays using micropython's framebuffer or even  a very basic one line  liquid crystal display.  

There is a root menu from which there can be any number of submenus. Each menuitem is associated with a simple python function which takes no parameters.  (If we want to supply parameters we can use default values or closures)

The menu-item's function can do useful things like flashing neopixels, or setting a clock.

Some of these activities may take a long time (if ever) to complete,  for instance neopixels flashing forever.  The system is  multitasking (using uasyncio)  so we can still run the menu itself,   at the same time as we are doing other activities..

Obviously to be useful, we have to write some functions for the menu actions.  In a real world program these have to be defined first because we cant use them until they are defined. As an introduction however we will start with defining a menu as this is the part that is new.


## Menu and Submenus

Menus are define as a list of menu-items.
A menu item is defined as a pair of values:

	1.  A Caption  (string)
	2. An action function (a python function with NO parameters)
	
A menu is defined as list of menu item pairs.

  ```python

trees     = wrap_menu( [('gum',data),('tea-tree',data),('red-gum count',data),('willow',data),('Back!',back)])

patterns  = wrap_menu( [('Chaser',yellow),('Red',red),('Blue',ablue),('Rainbow',rainbow),('Back!',back)])

main_menu = wrap_menu( [('Patterns',patterns),('trees',trees),('Brightness',brightness)])

```

Here we have defined three menus, 'trees', 'patterns' and 'main_menu'.
Note that the caption needs quotes (because it is a string), but the function does not (because it is just the name of a function.

To turn our list into a function we pass it to another function called 'wrap_menu'.  Since our menu is itself a function,  it can be the function that is called from another menu.  This way we can get sub-menus.

Note that since the main_menu with the caption "Patterns" calls the menu function patterns, we must define patterns before we define the main_menu.


### Functions to get information
Three functions to get information are pre-defined:
1. get_integer
2. get_selection
3. wizard

#### get_integer
This allows to set a number by twiddling the shaft of the encoder.  The number is entered by click and is stored in a global dictionary called data.
The key is set by the field parameter.

``` python
sethours   = get_integer(field = 'hour', low_v=1,high_v=24,increment=1,caption='Hours',field='hour')
```

Later the value can be retrieved as below:

``` python

if data['hour'] = 10:
	pass
	#Then do something

```

#### get_selection

The selection function lets us get a string value from a list of values. The list is similar to a menu's list.  There is also a field parameter.

```python 
colour1 = selection('colour1',['RED',('Green','GREEN'),('Blue','BLUE'),('Yellow','YELLOW'),('WHITE','white')])
```

As we turn the shaft the name of the various colours is displayed.  
When we click the shaft the current value is returned.  
The name displayed is the first value in the tuple and the value returned is the second element of the tuple.  
There is an option to just provide a string (say "RED"). 
In this case the string value is exanded to a tuple ('RED','RED') behind the scenes.

```python 
colour1 = selection('colour1',['RED',('Green','GREEN'),('Blue','BLUE'),('Yellow','YELLOW'),('WHITE','white')])

#color1 is the field parameter
```

#### Wizard and get_integer
In small microprocessor systems we often want to enter a series of numbers like hours, minutes and seconds to set a clock.  
The wizard calls a series of functions in sequence.  We define  a wizard  similarly to a menu.

timewizard = wizard([("Hours",sethours),("Minutes",setminutes),("Seconds",setseconds)])

This wizard will gather hours, minutes and seconds in that order,   then return.

sethours is a another function called  gets_integer with some parameters that (define as defaults parameters) for a caption, maximum value, minimum value. Increment  tells get_integer how much to expand the value on each click of the encoder.  
For instance if we set a percentage, 100 clicks is pretty tedious. 
We can set the encoder to return values between 0 and 10 and then expand the value by 10 by increment so we can get from 0 to 100 with 10 clicks.   

## How to get data out of the system.

Data is returned by the functions get_integer and selection.  
Each of these functions has a parameter called field.  
There is a global dictionary in the  encodermenu module called data and values are stored in this dictionary. 
It is up to you what you want do do with the values.

For instance in the selection above the field name is 'colour1'.  If we clicked on the screen while  it was showing 'RED' the dictionary would contain the folllowing
encodermenu.data['colour1'] = 'RED'

### How to set default values
We can set default values by setting the encodermenu.data before we run mainloop.  get_integer and selection  read the data dictionary, both when they are created and when they are revisited through the menu system to get the intial value.   The  current value in data is displayed, and  then can  be altered by scrolling.

If you do not provide a default value get_integer will default to zero (0) and selection will default to 'dummy'
  
 ### The info function.
 The info function just displays a screen of text which will be shown when you click its menuitem. Any click or scroll with clear the display (back to the menu).   You can provide the text as a simple string but you can also provide a function that returns a string.  This would allow you, for instance, to display the current time. These alternatives are show below

```python
showtime = info('I dont have a clock')
showtime = info(my_gettime_function)  
# don't use brackets on the function
```

 ##  Writing action functions.
 
There are several considerations so we will need to come back to this topic later.
At this stage you can just write a function as long as it is quick.
 
  ```python
  def  showblueneopixels():
      for a in range(smallnumber):
         do_something()
  ```
This will work  as a menu function.  The menu will be unchanged, which is usually fine, especially if your function is quick. 
However, if the function takes a long time to run it will block and the menu system will freeze.
We can get around blocking by writing an async function.  More on this later.



# How it works - some implementation details.

The system runs a bit like a gui.
There is a event loop that polls the switch and the encoder. 
If the switch is pressed or the value of the encoder changes then an on_click or on_scroll event is called.
Events are handled by an object, which can be a Menu, GetInteger, Selection, Info Wizard and so on.
The object handling the events is a global  called current.
We change menus and entry screens etc by changing the current object.
The main loop runs as an asyncio task so it does not block.
Any function called within the menu system is also running within the asyncio loop so it can be a task or routine.
A convenience function call make_task is provided which store the task in a global variable called task.
A second convenience function called stop can stop the running task.
(Note: This simple system with only handle one task. You can run more task but you will have to manange them himself).

When we click a menuitem with one of the predefined objects like Menu, GetInteger, Selection etc the object is putt on a stack.
There is a special function called back which pops the object off the stack so we can go back to where we came from.
Actually we could handle with another event called back.  You could provide this, if you want,  by polling for another switch.
I found that just having a back functions is quite intuitive and it is simple.

### Various issues
1. Be careful to define submenus before main parent menus.  If not you will get varibale not defined errors.
2. 



A menu is like a tree.  We start off on the trunk ("main_menu") and from this sub_menus branch off.  We can also branch off a submenu, so the menu can be arbitarily complex.   When we hit a leaf an action is performed. (Actually we can perform an action at any part of the tree but we will come back to that later.)

We have to write the main_menu last because it will refer to branchs above. In this case our display will show "Patterns" then "Trees" then "Brightness" as we turn the rotary encoder. If we click the "go" button (I use the switch on the shaft that comes with the encoder I used ) a function associated with the menu item will be executed. If we click on "Patterns" the patterns menu we defined in the line above will show.  Similarly for the "tees" menu. However if we click on Brightness we will excute a brightness function.  This allows us to enter an integer value for brightness. (More on this later).

### Going back up the menu 
If we click on a menu we go further into the tree down a branch,   or we hit a leaf.  But what if we want to go back up the tree?   In this simple Menu we go back back by executing a back function that pops us back at the first item in the previous menu. I find this is intuitive and works well plus it does not require any extra hardware.

An alternative would be to provide a back button.  Another alternative is to get some extra events off our simple button (like long-press or double click)  I will show how this can be done later. (The menu uses  uasyncio which  has  a good primitives libary from Peter Hinch that allows us to easily program for long presses or double clicks)

### Writing a menu (menus are functions and actions are functions)
We note that a menuitem is defined as tuple composed of a string menu item caption and an action that is performed if the menu is clicked, like so ('Caption1', action1).  A menu is a list of menu-items.  (Note - we could use either lists or tuples - it does not really matter).  

After we have provided a list of menu-items we have to wrap the list up into a function and we do this by using the wrap function.  This means that both actions and submenus are handled the same way in our system.  A submenu is simply an action that installs a new menu.

#### How to write and action or menu function.
Writing a menu or submenu is easy, - we just pass the list to the wrap funcion which does the work for us.

All menu functions (including submenus) are a function that takes one parameter. When the function is called the Menu class passes in self so that the function acts like like a temporary method of the Menu class.  This gives us access to other methods in the Menu class but we can ignore the self parameter if we dont need it. Although action functions only have one parameter it is possible to pass extra information via default values or literals inside our functions or closures. (Examples below) 

#### Builtin  methods
Some functions are  built in:
1. back - There is a back function that goes back up the menu
2. get_integer. This is an action that allows to enter an integer via the rotary encoder.  The value entered is stored in a data dictionary so it is available to other actions.
3. wrap.  This function takes a menu list and returns a menu function.


First some housekeeping because some of the setup may be a bit unfamiliar
We have to import some modules and get the menu running.

### Housekeeping

``` python
from encodermenu import Menu  #this the Menu class
from neopixel import * #We use neopixels as an example of menu actions
import neopixel

H = Menu()  # Make a menu object
#Remember main_menu is a function with one parameter 
# So we have to set it up like this....
main_menu(H)
#The menu runs asynchonously.  This means we can write long running actions without block the main menu.  
#It is not necessary to know about async programming to get started.
# Further information on async aspects of this program below

asyncio.run(H.mainloop())# Run our encoder and switch loop asynchonously

#Usually the program above will be in an endless loop.
print('finished - probably wont get here')
```
	
2. Write an async function.
  ``` python
async def  showblueneopixels():
	for a in range(smallnumber):
		do_something()
		await asyncio.sleep(0)
  ```

To turn an ordinary function into an async function put async before def  then sprinkle some await asyncio.sleep(0) statements to make it play nice with others.  
	
If you want more intelligent instruction than this there are plenty of tutorials to google.  Peter Hinchs tutorial is very good but does get moderately advanced.
	
This function will work with the menu system but will likely prevent you from running other functions.  To get around this we need to make a task.
	
3. Write an async task.
  ``` python 
  def my_task_function()
      stop()
 	    make_task(show_blue_pixels)
 ```
# ddd    
 The menu encoder module provides two utility functions for tasks.  The first one is stop(). This cancels  other running tasks (say a continually running rainbow on neopixels) and allows you start another one.  make_task makes a global task called task.  Stop stops that global task.  This allows you to run one long running function after another.
 
4. Running several long running functinons simultaneously. 
This can be done but is beyond the scope of this tutorial. Basically you give each function its own task.  If necessary,  then work out some way to stop them.  I would recommend Peters tutorial at this point.

5. Write a function that does something on the screen.  
There are a few possibilities.
	a. Quick function.  Just display something on the screen.  It will stay there until you scroll or click. 
	b.  One work around for a volatile display would be to adjust your display function so that is does not alter the bottom line of your display on scroll or click allowing a message to persist.
	c. Slow or async function.  Write something to the display from time to time.
	


### How to write  actions - by example

```python

num_pixels = 75  
    
# this is taken from the Pi Pico neopixel example
def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)
    
def ablue(self):
    "Menu function One way to call an async function"
    #This program is really quick so it does not really need to be
    #asynchonous.
    print('async blue')  #Just to show we got here
    self.stop()  # stop other async functions
    async def show_blue():  #This is pretty much the same as the exampel
        neopixel.pixels_fill(BLUE)
        pixels_show()
    self.t = asyncio.create_task(show_blue())

def blue(self):  #same thing as ablue but as anormal function
    "Menu function.  Ignores self and makes neopixels blue"
    print('in blue')
    self.stop()#Optional but we still should stop other tasks
    neopixel.pixels_fill(BLUE)
    pixels_show()

def red(self):  #Pretty much the same as ablue above
    print ('red')
    self.stop()
    async def temp():
        pixels_fill(RED)
        pixels_show()
    self.t =asyncio.create_task(temp())
        
def rainbow(self):
    "call an async function defined elsewhere"
    print('start rainbow')
    self.stop()
    #Shows a moving rainbow so can take a while.
    #This is the sort of function that we should make asynchronous
    #Note that we save the task as self.t so we can stop it if necessary
    self.t = asyncio.create_task(rainbow_cycle(self))


def yellow(self):  #Same as red and ablue only even more minimal
    neopixel.pixels_fill(YELLOW)
    neopixel.pixels_show()
    
async def rainbow_cycle(self):  # A full asynchronous loop
    "Show a rainbow but yield frequently for menus etc"
    self.stop() #stop other tasks
    for k in range(255):
        for j in range(255):
            for i in range(NUM_LEDS):
                rc_index = (i * 256 // NUM_LEDS) + j
                neopixel.pixels_set(i, wheel(rc_index & 255))
                await asyncio.sleep(0) # give someone else a go
            neopixel.pixels_show()
            await asyncio.sleep(0)# give someone else a go

#Now that we have some actions we can finally define some menus

trees     = wrap( [('gum',data),('tea-tree',data),('red-gum count',data),('willow',data),('Back!',back)])
patterns  = wrap( [('Chaser',yellow),('Red',red),('Blue',ablue),('Rainbow',rainbow),('Back!',back)])
main_menu = wrap( [('Patterns',patterns),('trees',trees),('Brightness',brightness)])

#Bit more housekeeping.
H = Menu()
main_menu(H) # This sets up the main or root menu
asyncio.run(H.mainloop())  #make it go

asyncio.run(blue(3))
print('finished')

```

## Source of Encoder menu class (with extra comments)

``` python 
import math
from machine import Pin, I2C
import ssd1306  # The display
#import sys 
#import time  #In case we want to do precise time extra 
import uasyncio as asyncio

#from guimenu importMenu
#import _thread

#I use a sparkfun encoder with a switch in the shaft.  There are also some  coloured LEDS in the transparent shaft but I dont use them
from rotary_irq_pico  import RotaryIRQ # The encoder library

switch = Pin(18,Pin.IN,Pin.PULL_DOWN)  # I use the shaft of the encoder as the switch to initiate menu actions

encoder = RotaryIRQ(pin_num_clk=12, 
              pin_num_dt=13, 
              min_val=0, 
              max_val=100, 
              reverse=False, 
              range_mode=RotaryIRQ.RANGE_WRAP,
              pull_up=True)
              
#I use a little OLED display
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


class Menu():
    def __init__(self):
        
        self.menu_stack =[] # parent menus - so we can go back
        self.menu = None  # store current menu
        self.data = {} # A dictionary to hold values we may enter
        #Things work slighlty differently when we are traversing the menu from when we are entering a number - so I "vector" clicking and scrolling
        self.do_scroll = self.menu_scroll
        self.do_click = self.menu_click
        self.do_show   = self.menu_show
        self.ar =[]       

    def mainloop(self):
        "An asynchronous main loop"
        #We only do scroll stuff or button clicks when they change
        self.old_v = self.value 
        self.old_switch = switch()
        self.do_show() #Make sure we show the menu when we first start up
        while True:
            await self.step()  #step is a coroutine so await it
    
    async def step(self):
        """Poll scroll and switch asynchonously
        so we can run something else like neopixels at the same time.
        do_scroll and do_switch are vectors 
        so they  can  be  changed 
        """
        #only handle the scroll value if it changes
        self.enc_v = self.value
        if self.enc_v != self.old_v:
            self.do_scroll()
            self.old_v = self.enc_v
        #Only do click action if switch is on AND it has changed    
        self.sw_v = switch()
        if self.sw_v != self.old_switch:
            if self.sw_v:
                self.do_click()
            self.old_switch = self.sw_v
            await asyncio.sleep_ms(200) #helps with debounce
        await asyncio.sleep(0)  #give someone else a go
    
    def text(self,txt):
        "Show some text"
        # This should work unaltered for any display that 
        # uses framebuffer
        #For any display clear it and show a line of text
        oled.fill(0)
        oled.text(txt,0,30)
        oled.show()
             
    def text2(self,txt1,txt2):
        """Two rows of text, built for get_integer(), 
        but not limited to this purpose"
        In get_integer txt1 is a caption, txt2 shows the current integer 				value"""
      # for a more display just keep stuff on one line
        oled.fill(0)
        oled.text(txt1,0,0)
        oled.text(txt2,0,30)
        oled.show()

#---------------------------------
    #A property just lets us refer to scroll value as self.value
    #rather than self._value or self.value()
    @property
    def value(self):
        return encoder._value
        
    @value.setter
    def value(self,value):
        "Get current scroll value"
        encoder._value = value
    
    def setscroll(self,min_v,max_v,inc_v,value):
        encoder.set(value,min_v,max_v)
        # NB increment is only used outside encoder in
        #this implemenattion       
        self.increment = inc_v        
    
    def menu_show(self):
        "Show the current menu item"
        self.text(self.menu[self.value][0])
        
    def set_menu(self,menu):
        #Set up for a menu using the encoder value and a switch click
        self.menu = menu
        # we need to put the menu on a stack so we can come back
        self.menu_stack.append(menu)  
        
        self.setscroll (0,len(menu)-1,1,0) #keep value within range       
        self.do_scroll = self.menu_scroll #set menu vector   
        self.do_click = self.menu_click #set click vector
        
        self.menu_show() # all done - now show the menu

    def menu_scroll(self):
        self.menu_show()
    
    def menu_click(self):
        "menuitem has caption and a function"
        #Execute the function, passing self to it
        (self.menu[self.value][1])(self)
  
 #Now define some useful methods to use as menus menu functions

    def back(self):
​       "go back up then menu by excuting this function     
        if len(self.menu_stack) > 1:
            #the current menu is on the stack so we have to pop it off
            #unless there is only the root menu on the stack
            self.menu_stack.pop()
        mymenu = self.menu_stack.pop()
        self.set_menu(mymenu)

#This allows us to enter a integer value and store it a data dictionary 
#belonging to the menu class
#By default the caption is show at top of the screen which does not change (say Brightness (%) for example) 
# The value is in the middle of the screen and changes as we turn the encoder.
# When we click the button the value is stored in our data field and we pop back to the menu.
#If we want to enter a percentage between 0 and 100 or some other large value it might be annoying to have to do 100 clicks.
# Increment allows us, for example, to do 10 clicks but display them as 10 to 100.


    def get_integer(self,low_v=0,high_v=10,increment=10, caption='plain',field='datafield'):
        #set data field
        self.field = field
        self.do_click = self.integer_click
        self.do_scroll = self.integer_show
        self.do_show = self.integer_show 
        self.caption = caption
        self.menu_stack.append(self.menu) 
        
        try:
            data = int(self.data.get(field,0))
            if data > high_v:
                data = high_v
            if data < low_v:
                data = low_v
        except:
            data = 0
            
        self.setscroll(low_v,high_v,increment,data)
        self.do_show()


​        

    def integer_show(self):
        """Show a caption and a value which changes on scroll"
        Increment allows us (for instance) to have  only 10 clicks to get to 100% instead of 100 clicks """
        self.text2(self.caption,str(self.value*self.increment))

    def integer_click(self):
        "Store the displayed value and go back up the menu"
        self.data[self.field]= self.value * self.increment
        
        #? await asyncio.sleep(50)
        time.sleep_ms(50) #yield and debounce a bit
        self.back() #always go back after click
        
    def stop(self):
        """Our routine (neopixels in this case) is stored in a task.
        That allows us to cancel it"""
        try:
            self.t.cancel()
        except:
            pass

# END OF MENU CLASS DEFINITION
```


We can export menugui methods as is.
 We have to wrap normal functions up so they look like a menu object method

```python
#Export some action functions we are likely to use.

def back(self):
    self.back()

#basic data function using sort of default values
#and a closure method of passing parameters
def data(self):
    low_v=0
    high_v=100
    increment=10
    caption='plain'
    field='datafield'
    print('In data')
    def wrap():
        self.get_integer(low_v,high_v,increment, caption,field)
    return wrap
    
#just an example of using the get_integer method with default values

def brightness(self):
    self.get_integer(low_v=0,high_v=10,increment=10,caption='Brightness(%)',field='brightness')

def wrap(mymenu):
    "wrap a list into a function so it can be set from within the menu"
    def mywrap(self):
        self.set_menu(mymenu)
    return mywrap
```
## Using uasync

I am learning asynchronous programming as I write this menu program.  These notes are based on my current understanding.  I do believe they are alternative facts but nevertheless   may need to be fact checked.  

1. Asynchronous functions run cooperatively and "yield" every so often so other functions can run.
2. We are not supposed to talk about "yielding" which is similar to but different from yielding in a generator.  Wating and giving some else a go is critical to synchronous programmng.  If we dont really need to wait but just let someone else have a go we can say  "asyncio.sleep(0)". We should say this instead of "yield"

1. Asynchronous programs run within a big loop.  They should set up as   big main function which controls everything else.  We actually run the main function by calling  "asyncio.run(main())" 

3. We can define coroutines anywhere we like.  We make a coroutine by putting async in front of normal funcion defintion.  A corouting usually has an await statement somewhere in it but does not have to.
A co-routine does not run until we await it. 
eg await asyncio.sleep(10)

4. We must define tasks within the main function (thus they will go out of scope if our main funtin finishes).  We can await them but we do not have to and they start up immediately without await when we create them.  We can store a task, as we do in the menu class as self.t = asyncio.create_task(fred().  This allows to stop or cancel a task.

Unlike a coroutine we do not have to await a task so it starts immediately.   Thus we can go and make another task or await a co-routine.  The various tasks then  will run concurrently.

4. Writing a cooperative multitasking action task.
	1. Write a normal function to do something, such as light up some neopixels.
	2. Put async in front of it to make it a coutine.
	3. Sprinkle some await async.sleep(0) or other await functions in such a way they get called frequently.  This makes our function (or co-routine) cooperative.
	4. Now write a menu action function with one parameter called self.
	5. Inside  this action function, stop previous tasks by calling
		self.t.cancel()
		Make a task using our co-routine and call it self.t as below
		self.t = async.create_task(light_pixels())
	6. There is  now a proper co-operative co-routine and a proper action function. We can use the action function in our menu definition.


```python
async def rainbow_cycle(self):
    "Show a rainbow but yield frequently for menus etc"
    #adapted from pi pico PIO example
    self.stop()#stop any previous tasks
    
    for k in range(255):  #This extra loop makes it run longer
        for j in range(255):
            for i in range(NUM_LEDS):
                rc_index = (i * 256 // NUM_LEDS) + j
                neopixel.pixels_set(i, wheel(rc_index & 255))
                await asyncio.sleep(0) #make it play nice with others
            neopixel.pixels_show()
            await asyncio.sleep(0) #even nicer
            
# now we can put rainbow_cycle (without the brackets) as a menu action
```
	
