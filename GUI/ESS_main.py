'''
main.py is where the actual main program is called. Each module class is called in the first lines.
serial port is opened between the arduino and RPi in order to get the module number connected to run the specific program
'''

import serial
from time import sleep

# import all module scripts 
from ESS_GUI_module_0 import *
from ESS_GUI_module_1 import *
from ESS_GUI_module_2 import *
from ESS_GUI_module_3 import *
from ESS_GUI_module_4 import *
from ESS_GUI_module_5 import *
from ESS_GUI_module_6 import *
from ESS_GUI_module_7 import *

import matplotlib.pyplot as plt
#import tkinter library for running the modules
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkfont

# error popup box
#if serial port cannot be opened pop up this error box
def spectrometer_disconnect():
    root = Tk()
    root.geometry('800x480')
    root.title("ESS System Interface")
    root.configure(bg = 'sky blue')
    message = Label(root, text = 'Spectrometer Not connected, Connect and try again', bg = 'sky blue', anchor = "center").pack()
    quit_button = Button(root, text = 'QUIT', command = root.destroy, fg = 'red').pack()

# after the serial port is opened read in the module number and run the corresponding program 
def run_program():
    sleep(2.5) # wait for a little to initialize serial connection

    #tell arduino to read in the module number 
    ser.write(b'module\n') 
    module = int(ser.readline().decode()) # read in the module number
    
    print(module)
    root = Tk()
    
    if module == 0:
        app = Module_0(root)
        
    elif module == 1:
        app = Module_1(root)

    elif module == 2:
        app = Module_2(root)
        
    elif module == 3:
        app = Module_3(root)
        
    elif module == 4:
        app = Module_4(root)
        
    elif module == 5:
        app = Module_5(root)
        
    elif module == 6:
        app = Module_6(root)
        
    elif module == 7:
        app = Module_7(root)
    
    root.mainloop()
    
# open up a serial to allow for reading in of module attachment
# two possible serial ports on raspberry pi
port = "/dev/ttyUSB0"
port2 = "/dev/ttyUSB1"
run_it = 0 # handler for starting programs

# try to open up port number 1 if it works call the run_program function
try:
    ser = serial.Serial(port, baudrate = 115200, timeout = 3)
    run_it = 1
    run_program()
except:
    pass


# if the first serial port doesnt work then try the second port2 to run program
# if both ports dont work then run the error function to popup error
if run_it == 1:
    pass
else:
    try:
        ser = serial.Serial(port2, baudrate = 115200, timeout =3)
        run_program()
    except serial.serialutil.SerialException:
        spectrometer_disconnect()

 
