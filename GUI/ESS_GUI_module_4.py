## tkinter used for widgets that make up GUI framework
from tkinter import *
import numpy as np #https://scipy-lectures.org/intro/numpy/operations.html
from tkinter import messagebox
import tkinter.font as tkFont

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

class Module_4:
    def __init__(self, master):
        global settings_file
        self.root = master
        self.root.title("ESS Module 4 Frame")
        full_screen = False
        if full_screen:
            self.root.attributes('-fullscreen', True) # fullscreen on touchscreen
        else:
            self.root.geometry('800x480') # actual size of RPi touchscreen
        #self.root.attributes('-fullscreen',True)
        self.root.configure(bg= "sky blue")
        self.root.minsize(800,480) # min size the window can be dragged to

        self.percent = 0 # battery percent variable
        self.battery_array = []
        self.charging = False
        self.open_loop_stop = None # control open Loop button
        battery_font = tkFont.Font(family = "Lucida Grande", size = 8)
        label_font = tkFont.Font(family = "Lucida Grande", size = 12)
        warning_font = tkFont.Font(family = "Lucida Grande", size = 24)
        # parameters for buttons and frames
        #create all the buttons onto to the main window
        button_width = 8
        button_big_height = 8
        button_small_height = 3
        sticky_to = 'nsew' # allows all buttons to resize
         
        # setup Serial port- 
         ## Graphing Frame and fake plot
        self.graph_frame = Frame(self.root, background = "white")
        self.graph_frame.grid(row = 1, column = 0, columnspan = 5, sticky ='nsew')
        
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
        
        self.open_new_button = Button(self.root, text = "New Experiment", wraplength = 80, fg = 'black', command = self.func.open_new_experiment, width = button_width, height = button_big_height)
        self.open_new_button.grid(row = 0, column = 0, padx = (0,1), sticky = sticky_to)
        
        self.open_experiment_button = Button(self.root, text = "Open Experiment", wraplength = 80, fg = 'black', command = self.check_scan_number_open_file, width = button_width, height = button_big_height)
        self.open_experiment_button.grid(row = 0, column = 1, sticky = sticky_to)
        
        self.module_label = Label(self.root, bg = 'sky blue', wraplength = 80, text = "Module 4: TBD", width = button_width, height = button_big_height)
        self.module_label.grid(row = 0, column = 4, padx = 1, sticky = 'nsew')
        
        # with all their corresponding functions (command)
        self.quit_button = Button(self.root, text = "Quit", fg = 'Red', command = self.quit_button, width = button_width, height = button_big_height)
        self.quit_button.grid(row = 0, column = 2, padx = 1, sticky = 'nsew')
        
        #battery Frame to show battery level and scan number
        self.battery_frame = Frame(self.root, bg = 'sky blue', width = 4)
        self.battery_frame.grid(row = 0, column = 3, sticky = 'nsew')
        
        # allow buttons and frames to resize with the resizing of the root window
        # need to change this to however many rows/columns you hav
        self.root.grid_columnconfigure((0,1,2,3,4),weight = 1)
        self.root.grid_rowconfigure((0,1),weight = 1)
        
        battery_width = 6
        
        self.battery_label_1 = Label(self.battery_frame, bg = "green", height = 1, width = battery_width)
        self.battery_label_1.grid(row = 0, column = 0, padx = 1, sticky = 'nsew')
        
        self.battery_label_2 = Label(self.battery_frame, text = "%", font = battery_font, height = 1, bg = "green", width = battery_width)
        self.battery_label_2.grid(row = 1, column = 0, padx = 1, sticky = 'nsew')
        
        self.battery_label_3 = Label(self.battery_frame, bg = "green", height = 1,width = battery_width)
        self.battery_label_3.grid(row = 2, column = 0, padx = 1, sticky = 'nsew')
        
        self.battery_label_4 = Label(self.battery_frame, bg = "green",height = 1, width = battery_width)
        self.battery_label_4.grid(row = 3, column = 0, padx = 1, sticky = 'nsew')
        
        self.scan_label = Label(self.battery_frame, bg = 'sky blue', text = "Scan: ", font = battery_font, height = 1, width = battery_width, wraplength = 80)
        self.scan_label.grid(row = 4, column = 0, padx = 1, sticky = 'nsew')
        
        self.battery_frame.grid_rowconfigure((0,1,2,3,4),weight = 1)
        self.battery_frame.grid_columnconfigure((0),weight = 1)
        
        # show module connected
        #messagebox.showinfo('Module #','Module 0: Base ESS System connected (No attachments)')
        
        # check battery percent from arduino
        def battery_percent_check():
            self.percent = self.func.battery_check()
            self.charging = False
            # check for charging and then add percent to array for averaging
            if int(self.percent) == 1000:
                self.charging = True
            self.battery_array.append(int(self.percent))
            if len(self.battery_array) > 10:
                del self.battery_array[0]
            
            #average battery_array
            self.percent = int(sum(self.battery_array)/(len(self.battery_array)))
            
            if self.charging:
                self.battery_label_1.configure(bg = 'green')
                self.battery_label_2.configure(font = battery_font, text = "Charging", bg = 'green')
                self.battery_label_3.configure(bg = 'green')
                self.battery_label_4.configure(bg = 'green')
            else:
                if int(self.percent) >=75:
                    
                    self.battery_label_1.configure(bg = 'green')
                    self.battery_label_2.configure(font = battery_font, text = str(self.percent) + " %", bg = 'green')
                    self.battery_label_3.configure(bg = 'green')
                    self.battery_label_4.configure(bg = 'green')
                
                elif int(self.percent) <75 and int(self.percent) >= 50:
                    self.battery_label_2.configure(font = battery_font, text = str(self.percent) + " %",bg = 'green')
                    self.battery_label_1.configure(bg = 'red')
                    self.battery_label_3.configure(bg = 'green')
                    self.battery_label_4.configure(bg = 'green')
                    
                elif int(self.percent) <50 and int(self.percent) >=25:
                    self.battery_label_1.configure(bg = 'red')
                    self.battery_label_2.configure(font = battery_font, text = str(self.percent) + " %",bg = 'red')
                    self.battery_label_3.configure(bg = 'green')
                    self.battery_label_4.configure(bg = 'green')
                    
                elif int(self.percent) < 25 and int(self.percent) >= 15:
                    self.battery_label_1.configure(bg = 'red')
                    self.battery_label_2.configure(font = battery_font, text = str(self.percent) + " %",bg = 'red')
                    self.battery_label_3.configure(bg = 'red')
                    self.battery_label_4.configure(bg = 'yellow')
                else:
                    self.battery_label_1.configure(bg = 'red')
                    self.battery_label_2.configure(font = battery_font, text = "LOW",bg = 'red')
                    self.battery_label_3.configure(bg = 'red')
                    self.battery_label_4.configure(bg = 'red')
                    
                    error_top = Toplevel(self.root, bg = "red")
                    message = Label(error_top, bg = "white", text = "Low Battery! Plug In device and Save Data", font = warning_font, wraplength = 250)
                    message.grid(row = 0, column = 0, padx = 10, pady = 10)
                    error_top.title("Warning")
                    error_top.lift()
                    
                    error_top.after(3000, error_top.destroy)


            try:
                self.root.after(10000, battery_percent_check)
            except:
                pass
            
        battery_percent_check()
        
        #show module number/info
        #messagebox.showinfo('Module #','Module 3: Module 3 Connected')
    def check_scan_number_open_file(self):
        message = self.func.OpenFile()
        self.scan_label.config(text = message)
        
    def quit_button(self):
        self.root.destroy()
        self.root.quit()
        
