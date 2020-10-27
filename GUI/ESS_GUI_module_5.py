## tkinter used for widgets that make up GUI framework
from tkinter import *
import numpy as np #https://scipy-lectures.org/intro/numpy/operations.html
from tkinter import messagebox

#import all dependancies
from settings import Settings as _Settings
from ESS_functions import *
from keyboard import *
#from settings_window import settings_popup_window
import settings_window

# create new files and folders
import os

#used for serial comm with arduino
import serial
from time import sleep
import time
 
#saving data to csv
import pandas as pd
import csv

### matplotlib used for plotting data to a canvas 
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot as plt


################ global variables ###########################
spec_folder_path = '/home/pi/Desktop/Spectrometer'
spec_folder_settings = '/home/pi/Desktop/Spectrometer/settings'
settings_file = '/home/pi/Desktop/Spectrometer/settings/settings.csv'
acquire_file = '/home/pi/Desktop/Spectrometer/settings/acquire_file.csv'


####################################################################


# create folder to hold all settings and data
if not os.path.exists(spec_folder_path):
        os.makedirs(spec_folder_path)
                
if not os.path.exists(spec_folder_settings):
        os.makedirs(spec_folder_settings)
# create acquire pseudo file if not already within spectrometer folder

try:
    #acquire file holds a temporary data array
    open_acquire_file = open(acquire_file, 'x')
except:
    open_acquire_file = open(acquire_file, 'a')
# open up a serial to allow for reading in of module attachment

class Module_5:
    def __init__(self, master):
        global settings_file
        self.root = master
        self.root.title("ESS Module 5 Frame")
        full_screen = False
        if full_screen:
            self.root.attributes('-fullscreen', True) # fullscreen on touchscreen
        else:
            self.root.geometry('800x480') # actual size of RPi touchscreen
        #self.root.attributes('-fullscreen',True)
        self.root.configure(bg= "sky blue")
        self.root.minsize(800,480) # min size the window can be dragged to

        
        self.open_loop_stop = None # control open Loop button
        
        # parameters for buttons and frames
        #create all the buttons onto to the main window
        button_width = 10
        button_big_height = 4
        button_small_height = 3
        sticky_to = 'nsew' # allows all buttons to resize
         
        # setup Serial port- 
         ## Graphing Frame and fake plot
        self.graph_frame = Frame(self.root, background = "white")
        self.graph_frame.grid(row = 2, column = 0,sticky = sticky_to)
        
        #initalize figure
        self.fig = plt.figure()
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('ADC Counts')
        plt.xlim(300,900)
        plt.ylim(0,66500)
        plt.subplots_adjust(bottom =0.14, right = 0.95, top = 0.96)
        
        #initalize canvas for plotting
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)  # A tk.DrawingArea.
        # create toolbar for canvas
        toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill = BOTH, expand = True)
        
        # create function object for calling functions
        settings_func = _Settings(settings_file)
        
        try:
            settings_func.create_settings()
        except:
            pass
        
        
        self.func = functions(self.root, self.canvas, self.fig)
        
        # allow buttons and frames to resize with the resizing of the root window
        # need to change this to however many rows/columns you hav
        self.root.grid_columnconfigure((0),weight = 1)
        self.root.grid_rowconfigure((0,1,2),weight = 1)
        
        # with all their corresponding functions (command)
        self.quit_button = Button(self.root, text = "Quit", fg = 'Red', command = self.quit_button, width = button_width, height = button_big_height)
        self.quit_button.grid(row = 1, column = 0, padx = 1, sticky = sticky_to)
        
        #show module number and info
        #messagebox.showinfo('Module #','Module 5: Module 5 Connected')
        
    def quit_button(self):
        self.root.destroy()
        self.root.quit()
        