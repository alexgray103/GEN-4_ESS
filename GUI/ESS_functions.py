from tkinter import *
from tkinter.ttk import *
import matplotlib.pyplot
import time

import serial
from settings import Settings as _Settings
from keyboard import *
from add_remove_popup import *

import pandas as pd
import numpy as np
import csv
from tkinter import messagebox

from tkinter.filedialog import askopenfilename
import os
import matplotlib.pyplot as plt


################# Global Variables ############################
global settings_file
global acquire_file
global path

settings_file = '/home/pi/Desktop/Spectrometer/settings/settings.csv'
acquire_file = '/home/pi/Desktop/Spectrometer/settings/acquire_file.csv'
path = '/home/pi/Desktop/Spectrometer/'
#################################################################


class functions:
    def __init__(self, parent, _canvas, figure):
        global settings_file
        global acquire_file
        global ESS_module
        self.parent = parent # whatever parent 
        self.save_file = None # initalize file for saving data
        self.scan_file = None #initialize Scan File for saving scan data
        self.scan_number = 1 # ID for saving to csv
        self.reference_number = 1 # ref ID for saving to csv
        self.exp_folder = '/home/pi/Desktop/Spectrometer' # experiment folder used for saving
        self.df = None # data frame array used for storing and plotting data
        self.df_scan = None
        self.serial_check = False #variable for flagging serial connection
        self.battery_check_flag = False
        self.battery_percent = 100
        
        # attributes to select data to be plotted
        self.ref = np.ones((288))*1000 # temporary reference
        self.scan_ref = None
        
        # plotting view attributes
        self.ratio_view_handler = False
        self.autoscale_handler = False
        self.prime_pump_handler = False  # handle turning on/off pump
            
        # these are two possible port names for the arduino attachment
        port = "/dev/ttyUSB0"
        port2 = "/dev/ttyUSB1"
        
        try:
            self.ser = serial.Serial(port, baudrate = 115200, timeout = 5)
        except:
            self.ser = serial.Serial(port2, baudrate = 115200, timeout =5)
        
        # two pseudo reads to initalize the spectrometer
        self.ser.write(b"read\n")
        data = self.ser.readline()
        self.ser.write(b"read\n")
        data = self.ser.readline()
        
        
        # intialize attributes for handling data and files
        self.acquire_file = acquire_file
        self.settings_file = settings_file
        self.canvas = _canvas
        self.fig = figure
        
        # create objects for different modules needs for some functions
        self.settings_func = _Settings(settings_file)
        (self.settings, self.wavelength) = self.settings_func.settings_read()
        self.add_remove_top = add_remove_popup(self.parent)
        
    def home(self):
        self.ser.write(b"home\n")
        
    def battery_check(self):
        if not self.battery_check_flag:
            self.ser.write(b"battery\n")
            percent = self.ser.readline().decode()
            self.battery_percent = percent
            return percent
        else:
            return self.battery_percent
    
    def save_scan_reference(self):
        if self.scan_file is not None:
            self.scan_ref = pd.DataFrame(np.loadtxt(self.acquire_file, delimiter = ','))
            self.df_scan['Reference %d'] = self.scan_ref
            self.df_scan.to_csv(self.scan_file, mode = 'w', index = False)
        else:
            messagebox.showerror('Error', 'No Save File selected, create save file to save reference')
        
    def save_reference(self):
        ref_message = None
        if self.save_file is not None:
            self.ref = pd.DataFrame(np.loadtxt(self.acquire_file, delimiter = ','))
            self.df['Reference %d' % self.reference_number] = self.ref
            self.df.to_csv(self.save_file, mode = 'w', index = False)
            self.reference_number = self.reference_number +1 
            ref_message = "Ref #: " + str(self.reference_number-1)
            self.ref = self.ref.to_numpy().reshape((288))
            plt.clf()
            self.plotting(np.zeros((288)), None) # send a fake value to plot updated ref
            
        else:
            messagebox.showerror('Error', 'No Save File selected, create save file to save reference')
        return ref_message
    
    def save_spectra(self):
        scan_message = None
        if self.save_file is not None:
            temp_data = pd.DataFrame(np.loadtxt(self.acquire_file, delimiter = ','))
            self.df['Scan_ID %d' % self.scan_number] = temp_data
            self.df.to_csv(self.save_file, mode = 'w', index = False)
            scan_message = "Scan: " + str(self.scan_number)
            self.scan_number = self.scan_number +1 
        else:
            messagebox.showerror('Error', 'No Save File selected, create save file to save Spectra')
        return scan_message
    
    def add_remove_func(self):
        self.add_remove_top.create_add_remove(self.save_file)
        
        if self.add_remove_top.ref_ratio is not None:
            self.ref = self.df[[self.add_remove_top.ref_ratio]].to_numpy() 
        
    def ratio_view(self):
        self.ratio_view_handler = not self.ratio_view_handler
    
    def autoscale(self):
        self.autoscale_handler = not self.autoscale_handler
        if self.autoscale_handler:
            plt.autoscale(enable= True, axis = 'y')
            self.fig.canvas.draw()
        elif not self.autoscale_handler and self.ratio_view_handler:
            plt.autoscale(enable = False, axis = 'y')
            plt.ylim(0,110)
            self.fig.canvas.draw()
        else:
            plt.autoscale(enable = False, axis = 'y')
            plt.ylim(0,66500)
            self.fig.canvas.draw()
    
    def plot_labels_axis(self):
        plt.subplots_adjust(bottom =0.14, right = 0.95, top = 0.96)

        if self.ratio_view_handler:
        
            plt.plot(self.wavelength, np.ones((288))*100, 'r--')
            if not self.autoscale_handler:
                plt.ylim(0,110)
            plt.xlim(300,900)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Ratio (%)')
        elif not self.ratio_view_handler:
            if not self.autoscale_handler:
                plt.ylim(0,66500)
            plt.xlim(300,900)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('ADC counts')
        #self.fig.canvas.draw()
        
    def plotting(self, data, label_view):
        
        data = pd.DataFrame(data).to_numpy().reshape((288))
        self.plot_labels_axis() # configure axis
        if self.ratio_view_handler:
            plt.clf()
            self.plot_labels_axis() # configure axis
            
            if self.add_remove_top.ref_ratio is not None:
                self.ref = self.df[[self.add_remove_top.ref_ratio]].to_numpy()
                self.ref = self.ref.reshape((288))
            try:
                self.ref = self.ref.to_numpy().reshape((288))
            except:
                pass

            data = np.true_divide(data, self.ref)*100
            if self.add_remove_top.data_headers is not None:
                data_sel = pd.read_csv(self.save_file, header = 0)
                data_sel = data_sel[self.add_remove_top.data_headers]
                for col in range(0, len(self.add_remove_top.data_headers)):
                    data_new = data_sel[str(self.add_remove_top.data_headers[col])]
                    data_new = data_new.to_numpy()
                    data_plot = np.true_divide(data_new, self.ref)*100
                    plt.plot(self.wavelength, data_plot, label = self.add_remove_top.data_headers[col])
                #plt.legend(self.add_remove_top.data_headers, loc = "upper right", prop = {'size': 6})
        else:
            if self.add_remove_top.data_headers is not None:
                data_sel = pd.read_csv(self.save_file, header = 0)
                data_sel = data_sel[self.add_remove_top.data_headers]
                for col in range(0,len(self.add_remove_top.data_headers)):
                    plt.plot(self.wavelength, data_sel.iloc[:,col], label = self.add_remove_top.data_headers[col])
       
                #for col in range(0,len(self.add_remove_top.data_headers)):
                #plt.legend(self.add_remove_top.data_headers, loc = "upper right", prop = {'size': 6})
            else:
                pass
            
            try:
                self.ref = self.ref.to_numpy()
                plt.plot(self.wavelength,self.ref, 'r--', label = 'Reference')
            except:
                plt.plot(self.wavelength,self.ref,'r--', label = "Reference")
                
        plt.plot(self.wavelength, data, label = label_view)
        plt.xlim(int(self.settings[9][1]), int(self.settings[10][1]))
        plt.legend()
        self.fig.canvas.draw()
        
    def open_new_experiment(self):
        global path
        keyboard = key_pad(self.parent)
        try:
            (save_file, save_folder) = keyboard.create_keypad()
            self.save_file = save_folder + '/' + save_file + "_save.csv"
        
            self.exp_folder = str(save_folder)
            if not os.path.exists(self.exp_folder):
                os.makedirs(self.exp_folder)
        
            open(self.save_file, 'w+')
            
            #reset add_remove attributes
            self.add_remove_top.data_headers = None
            self.add_remove_top.data_headers_idx = None
            self.add_remove_top.ref_ratio_idx = None
            self.add_remove_top.ref_ratio = None
            
            #create data frame for saving data to csv files
            self.df = pd.DataFrame(self.wavelength)
            self.df.columns = ['Wavelength (nm)']
            save_csv = self.df.to_csv(self.save_file, mode = 'a', index=False)
            # reset scan and ref number for saving data when new file created
            self.scan_number = 1
            self.reference_number = 1
            
        except NameError:
           messagebox.showerror("Error", "No Filename Found! Please input again to create Experiment")
                       
    def plot_selected(self):
        plt.clf()
        self.plot_labels_axis()
        
        if self.add_remove_top.data_headers is not None:
            self.plotting(np.zeros((288)), None)
        else:
            messagebox.showerror('Error','No data selected. Select data to plot')
    
    
    def clear(self):
        plt.clf()
        plt.ylim(0,66500)
        plt.xlim(300,900)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('ADC Counts')
        self.fig.canvas.draw()
        
        
        
    def dark_subtract_func(self):
        self.battery_check_flag = True
        #(self.settings, self.wavelength) = self.settings_func.settings_read()
        number_avg = int(self.settings[11][1])
        integ_time = float(self.settings[3][1])
        smoothing_used = int(self.settings[12][1])
        smoothing_width = int(self.settings[8][1])
        pulses = int(self.settings[1][1])
        dark_subtract = int(self.settings[4][1])
        pulse_rate = int(self.settings[2][1])
        try:
            self.ser.write(b"pulse 0\n")
            self.ser.write(b"set_integ %0.6f\n" % integ_time)
            self.ser.write(b"pulse_rate %0.6f\n" % pulse_rate)
            # tell spectromter to send data
            data = 0
            data_dark = 0
            #for x in range(0,1,1): #take scans then average for dark subtract
            self.ser.write(b"read\n")
            #read data and save to pseudo csv to plot
            data_read = self.ser.readline()
            #data = self.ser.read_until('\n', size=None)
            data_dark = np.array([int(i) for i in data_read.split(b",")])
            
            #if x == 0:  # reached number of averages
            #data_dark = data_dark #take average of data and save
            #if smoothing_used == 1:  # if smoothing is checked smooth array
            #    dummy = np.ravel(data_dark)
            #    for i in range(1,286,1):
            #        data_dark[i] = sum(dummy[i-1:i+2])/(3)
            self.battery_check_flag = False
            return data_dark
        except serial.serialutil.SerialException:
            self.battery_check_flag = False
            messagebox.showerror('Error', 'Spectrometer Not connected, Connect and restart')
    
    def acquire_avg(self, pulses):
        self.battery_check_flag = True        
        #(self.settings, self.wavelength) = self.settings_func.settings_read()
        number_avg = int(self.settings[11][1])
        integ_time = float(self.settings[3][1])
        smoothing_used = int(self.settings[12][1])
        smoothing_width = int(self.settings[8][1])
        dark_subtract = int(self.settings[4][1])
        pulse_rate = int(self.settings[2][1])
        
        #self.serial_check = self.check_serial() # always check serial before a measurement
        #if self.serial_check:
        if dark_subtract == 1:
            data_dark = self.dark_subtract_func()
        else: 
            data_dark = np.zeros((288))
        try:        
            self.ser.write(b"set_integ %0.6f\n" % integ_time)
            self.ser.write(b"pulse %d\n" % pulses)
            self.ser.write(b"pulse_rate %0.6f\n" % pulse_rate)        
            # tell spectromter to send data
            data = 0
            for x in range(0,number_avg,1): #take scans then average
                
                self.ser.write(b"read\n") # tell arduino to read spectrometer
                data_read = self.ser.readline()
                data_temp = np.array([int(p) for p in data_read.split(b",")])
                data = data + data_temp 
                    
                if x == number_avg-1:  # reached number of averages
                    data = data/number_avg #take average of data and save
                    data = data-data_dark
                    if smoothing_used == 1:  # if smoothing is checked smooth array
                        dummy = np.ravel(data)
                        for i in range(1,286,1):
                            data[i] = sum(dummy[i-1:i+2])/(3)
            self.battery_check_flag = False
            data = np.where(data<=0,0,data)
            #for idx in range(0,len(data)):
            #    if data[idx] <=0:
            #        data[idx] = 1
            return data
        except serial.serialutil.SerialException:
            self.battery_check_flag = False
            messagebox.showerror('Error', 'Spectrometer Not connected, Connect and Restart')
            return None
    
    def acquire(self, save):
        scan_message = None
        (self.settings, self.wavelength) = self.settings_func.settings_read()
        
        data = self.acquire_avg(int(self.settings[1][1]))
        if data is not None:
            if save:
                if self.save_file == None:
                    messagebox.showerror('Error', 'No Experiment File Found, create or open File to save Data')
                else:
                    # save data array to save_file
                    df_data_array = pd.DataFrame(data)
                    self.df['Scan_ID %d' %self.scan_number] = df_data_array
                    self.df.to_csv(self.save_file, mode = 'w', index = False)
                    data = self.df[['Scan_ID %d' %self.scan_number]]
                    self.scan_number = 1 + self.scan_number
                    scan_message = "Scan #: " + str(self.scan_number-1)
                    plt.clf()
                    self.plotting(data, "Scan: " +str(self.scan_number-1))
            else: # temporary save
                np.savetxt(self.acquire_file, data, fmt="%d", delimiter=",")
                data = pd.read_csv(self.acquire_file, header = None)
                plt.clf()
                self.plotting(data, "Scan: " +str(self.scan_number))
                
            
        return scan_message
    
    def open_loop_function(self):
        if self.ser.is_open:
            (self.settings, self.wavelength) = self.settings_func.settings_read()
            plt.xlim(int(self.settings[9][1]), int(self.settings[10][1]))
            plt.ylabel('ADC counts')
            plt.xlabel('Wavelength (nm)')
            
            plt.clf()
            dark_subtract = int(self.settings[4][1])
            self.settings[4][1] = 0
            data = self.acquire_avg(0)
            self.settings[4][1] = dark_subtract
            data = pd.DataFrame(data)
            np.savetxt(self.acquire_file, data, fmt="%d", delimiter= ",")
            self.plotting(data, "Open Loop")
        
    def sequence(self, save):
        scan_message = None 
        if self.ser.is_open:
            (self.settings, self.wavelength) = self.settings_func.settings_read()       
            # make sure we have a save destination if acquire and save
            if save and self.save_file == None:
                messagebox.showerror('Error', 'No Experiment File Found, create or open File to save Data')
    
            else:
                plt.clf()
                number_avg = int(self.settings[11][1])
                integ_time = int(self.settings[3][1])
                dark_subtract = int(self.settings[4][1])
                burst_number = int(self.settings[22][1])
                burst_delay = float(self.settings[21][1])
                                
                plt.xlim(int(self.settings[9][1]), int(self.settings[10][1]))
                self.plot_labels_axis() # configure axis
                for burst in range(0,burst_number):
                    number_measurements_burst = int(self.settings[23+burst][1])
                    measurement = 0 # hold measurement number for each burst
                    pulses = int(self.settings[33+burst][1])
                    
                    #set integ time
                    self.settings[3][1] = float(120 + (pulses - 1)*(1000000/int(self.settings[2][1])))
                    if pulses > 1:
                        self.settings[3][1] = float(self.settings[3][1] + 1000000/int(self.settings[2][1]))
                    # take a dark measurement before each burst
                    if dark_subtract ==1:
                        self.settings[4][1] = 0
                        #dark = self.dark_subtract_func()
                        dark = self.acquire_avg(0)
                    else:
                        dark = np.zeros((288))
                    
                    for i in range(0,number_measurements_burst):
                        graph_label = 'Burst ' + str(burst+1) + ' measurement ' + str(i+1)
                        data = []
                        pulses = int(self.settings[33+burst][1])
                        data = self.acquire_avg(pulses)
                        data = data - dark
                        data = np.where(data<=0,0,data)
                        #check if we are in ratio view
                        if self.ratio_view_handler:
                            data = np.true_divide(data, self.ref)*100
                        data = pd.DataFrame(data).to_numpy()
                        
                        plt.plot(self.wavelength, data, label = graph_label)
                        plt.subplots_adjust(bottom = 0.14, right = 0.95)
                        plt.legend(loc = "center right", prop = {'size': 6})
                        
                        
                        
                        if save:
                            df_data_array = pd.DataFrame(data)
                            self.df['Scan_ID %d' % (self.scan_number)] = df_data_array
                            
                            self.scan_number = self.scan_number + 1
                            measurement = measurement+1 
                    self.settings[4][1] = dark_subtract
                    self.settings[3][1] = integ_time
                    self.fig.canvas.draw()
                    time.sleep(burst_delay)
                # after all data is taken save to sequence csv
                if save:
                    self.df.to_csv(self.save_file, mode = 'w', index = False)
                scan_message = "Scan: " + str(self.scan_number-1)
        return scan_message
    
    def autorange(self):
        (self.settings, self.wavelength) = self.settings_func.settings_read()       
        max_autorange = int(self.settings[7][1])
        autorange_thresh = int(self.settings[6][1])
        integ_time = int(self.settings[3][1])
        pulses = 1 # start with one pulse then increment
        plt.clf()
        
        plt.xlim(int(self.settings[9][1]), int(self.settings[10][1])) # change x axis limits to specified settings
        plt.ylabel('a.u.')
        plt.xlabel('Wavelength (nm)')
        # acquire data for the given # of loops plot, and prompt user to
        # select plots they wish to save with a popup window
        if self.ser.is_open:
            for x in range(0,max_autorange): 
                self.settings[1][1] = int(pulses)
                # write settings array to csv 
                self.settings_func.settings_write(self.settings)
                data = self.acquire_avg(pulses)
                if max(data) < autorange_thresh:  
                    if x < max_autorange-1:
                        pulses = pulses+1
                        plt.plot(self.wavelength,data, label = "Pulses: "+ str(self.settings[1][1]))
                        plt.subplots_adjust(bottom=0.14, right=0.86)
                        plt.legend(loc = "center right", prop={'size': 7}, bbox_to_anchor=(1.18, 0.5))
                        self.fig.canvas.draw()
                    else: 
                        messagebox.showinfo("Pulses", "Max # of Pulses reached")
                else:
                    self.settings[1][1] = int(pulses-1)
                    messagebox.showinfo("Pulses", str(self.settings[1][1]) + "  Pulses to reach threshold")
                    break
            self.settings_func.settings_write(self.settings)
            
    def OpenFile(self):
        scan_message = None    
        save_file = askopenfilename(initialdir="/home/pi/Desktop/Spectrometer",
                                    filetypes =(("csv file", "*.csv"),("All Files","*.*")),
                                    title = "Choose a file.")
        #try:
        if save_file: # check if file was selected if not dont change experiment file
            self.save_file = save_file 
            self.reference_number = 1
            self.scan_number = 1
            
            # try to scan through reference and scan number to set to correct value for further saving
            self.df = pd.read_csv(self.save_file, header = 0)
            headers = list(self.df.columns.values)
    
        #find the scan number from the opened file
        # only works for files with the specified headers
            while True:
                result = [i for i in headers if i.startswith('Scan_ID %d' %self.scan_number)]
                if result == []:
                    break
                self.scan_number = self.scan_number+1 # increment scan number until we reach correct value
            while True:
                result = [i for i in headers if i.startswith('Reference %d' %self.reference_number)]
                if result == []:
                        break
                self.reference_number = self.reference_number+1
                self.ref = pd.DataFrame(self.df['Reference %d' %(self.reference_number-1)]).to_numpy()
            self.ref = self.ref.reshape((288))
            

            #reset indexing attrubtues for later use in
            #add remove functions 
            self.add_remove_top.data_headers_idx = None
            self.add_remove_top.data_headers = None
            self.add_remove_top.ref_ratio = None
            self.add_remove_top.ref_ratio_idx = None
            scan_message = "Scan #: " + str(self.scan_number-1)
        return scan_message
    
    def new_scan(self):
        global path
        keyboard = key_pad(self.parent)
        self.df_scan = None
        try:
            (scan_file, save_folder) = keyboard.create_keypad()
            self.scan_file = save_folder + '/' + scan_file + "_scan.csv"
        
            self.exp_folder = str(save_folder)
            if not os.path.exists(self.exp_folder):
                os.makedirs(self.exp_folder)
        
            open(self.scan_file, 'w+')
            
            #create data frame for saving data to csv files
            self.df_scan = pd.DataFrame(self.wavelength)
            self.df_scan.columns = ['Wavelength (nm)']
            save_csv = self.df_scan.to_csv(self.scan_file, mode = 'a', index=False)
            
        except NameError:
           messagebox.showerror("Error", "No Filename Found! Please input again to create Experiment")
        except FileExistsError:
           messagebox.showerror("Error", "Filename Already Exists. Try New Filename")
        
    def scan(self):
        grid_size = int(self.settings[14][1])
        # check if spectrometer is connected
        
            
        if self.ser.is_open:
            self.ser.write(b"step_size %d\n" %int(self.settings[13][1]))        
            
            self.plot_labels_axis() # set axis and labels
            (self.settings, self.wavelength) = self.settings_func.settings_read()
            # if we dont have a scan file then create one for saving data
            if self.scan_file == None:
                messagebox.showerror('Error', 'No Scan File. Create scan file to save data')
            elif self.scan_file is not None:
                if self.scan_ref is not None:
                    for x in range(0,int(grid_size/2)):
                        self.ser.write(b"x 1\n")
                    time.sleep(1)
                    for y in range(0,int(grid_size/2)):
                        self.ser.write(b"y 1\n")
                    grid_size = int(self.settings[14][1])
                    scan_resolution = int(self.settings[13][1])
                    start = time.time()
                            
                    
                    def scan_move():
                        self.ser.write(b"step_size %d\n" %scan_resolution)
                        
                        for x in range(0,grid_size):
                            for y in range(0,grid_size):
                                idx = (x*grid_size) + y
                                            
                                data = self.acquire_avg(int(self.settings[1][1]))
                                df_data_array = pd.DataFrame(data)
                                if y == grid_size-1:
                                    if (x % 2) == 0:
                                        idx = (x*grid_size) + y
                                        self.df_scan['X: %d Y: %d' % (x, y)] = df_data_array
                                    else:
                                        idx = (x*grid_size) + grid_size - y -1
                                        self.df_scan['X: %d Y: %d' % (x, grid_size-y-1)] = df_data_array
               
                                else: 
                                    if (x % 2) == 0:
                                        idx = (x*grid_size) + y
                                        self.ser.write(b"y 0\n") # move in y after one scan
                                        self.df_scan['X: %d Y: %d' % (x, y)] = df_data_array

                                    else:
                                        idx = (x*grid_size) + grid_size - y -1
                                        self.ser.write(b"y 1\n")
                                        self.df_scan['X: %d Y: %d' % (x, grid_size-y-1)] = df_data_array
                                
                                self.button[idx].configure(bg = 'Green')
                                self.parent.update_idletasks()
                                self.progress_popup.update_idletasks()


                            self.ser.write(b"x 0\n")
                        
                        self.ser.write(b"home\n")
                        self.progress_popup.destroy()
                        plt.plot(self.wavelength, self.df_scan)
                        self.fig.canvas.draw()
                        self.df_scan.to_csv(self.scan_file, mode = 'w', index = False)
                        self.scan_file = None
                        end = time.time()
                        print(end-start)
                        
                    self.progress_popup = Toplevel(self.parent, bg = 'sky blue')
                    self.progress_popup.focus_force()
                    self.progress_popup.geometry('450x450')
                    self.button = list(range(0,grid_size**2 +1))
                    
                    for x_button in range(0,grid_size):
                        for y_button in range(0, grid_size):
                            idx = (x_button*grid_size) + y_button
                            self.button[idx] = Button(self.progress_popup, bg = 'red', width = 1, height = 1)
                            self.button[idx].grid(row = 1+y_button, column = x_button, sticky = 'nsew')

                    start_button = Button(self.progress_popup, fg = 'black', command = scan_move,
                                          width = 5, height = 3, text = 'Scan')
                    start_button.grid(row = 0, column = 0, columnspan = grid_size)
                    
    
                    #self.progress_popup.rowconfigure(0, weight = 2)
                    self.progress_popup.columnconfigure(0, weight =1)
                    for i in range(1,grid_size+1):
                        self.progress_popup.rowconfigure(i, weight = 1)
                        self.progress_popup.columnconfigure(i-1, weight =1) 
                else:
                    messagebox.showerror('Error', 'No reference Saved, Save Reference before Scanning')
        else:
            messagebox.showerror('Error','Spectrometer Not Connected, Connect and Restart')
                
               
########### Module 2 Functions ########################
    def pump_prime(self):
        self.prime_pump_handler = not self.prime_pump_handler
        self.ser.write(b"prime_pump %d\n" %self.prime_pump_handler)
        
    def water_acquire(self, save):
        scan_message = None
        (self.settings, self.wavelength) = self.settings_func.settings_read()
        self.ser.write(b"pump_read\n")
        data = self.acquire_avg(int(self.settings[1][1]))
        if data is not None:
            if save:
                if self.save_file == None:
                    messagebox.showerror('Error', 'No Experiment File Found, create or open File to save Data')
                else:
                    # save data array to save_file
                    df_data_array = pd.DataFrame(data)
                    self.df['Scan_ID %d' %self.scan_number] = df_data_array
                    self.df.to_csv(self.save_file, mode = 'w', index = False)
                    data = self.df[['Scan_ID %d' %self.scan_number]]
                    self.scan_number = 1 + self.scan_number
                    scan_message = "Scan #: " + str(self.scan_number-1)    
            else: # temporary save
                np.savetxt(self.acquire_file, data, fmt="%d", delimiter=",")
                data = pd.read_csv(self.acquire_file, header = None)
                
            plt.clf()
            self.plotting(data, "Scan: " +str(self.scan_number-1))
        return scan_message
    
    def water_sequence(self, save):
        seq_message = None
        plt.clf()
        if self.ser.is_open:
            if save and self.save_file == None:
                messagebox.showerror('Error', 'No Experiment File Found, create or open File to save Data')
            (self.settings, self.wavelength) = self.settings_func.settings_read()       
            number_avg = int(self.settings[11][1])
            integ_time = int(self.settings[3][1])
            smoothing_used = int(self.settings[12][1])
            smoothing_width = int(self.settings[8][1])
            dark_subtract = int(self.settings[4][1])
            burst_number = int(self.settings[22][1])
            burst_delay = float(self.settings[21][1])
            
            plt.xlim(int(self.settings[9][1]), int(self.settings[10][1]))
            self.plot_labels_axis() # configure axis
            start = time.time()
            for burst in range(0,burst_number):
                number_measurements_burst = int(self.settings[23+burst][1])
                self.ser.write(b"pump_read\n")
                for i in range(0,number_measurements_burst):
                    graph_label = 'Burst ' + str(burst+1) + ' measurement ' + str(i+1)
                    pulses = int(self.settings[33+burst][1])
                    data = []
                    data = self.acquire_avg(pulses).reshape((288))
                    data = pd.DataFrame(data)
                    if self.ratio_view_handler:
                        data = (data/self.ref)*100
                    data = pd.DataFrame(data).to_numpy()
                    plt.plot(self.wavelength, data, label = graph_label)
                    plt.subplots_adjust(bottom = 0.14, right = 0.95)
                    plt.legend(loc = "center right", prop = {'size': 6})
                    
                    if save:
                        seq_message = "Scan: " + str(self.scan_number)
                        df_data_array = pd.DataFrame(data)
                        self.df['Scan_ID %d' % (self.scan_number)] = df_data_array
                        self.scan_number = self.scan_number +1
                    else:
                        seq_message = "Scan: Temp"
                time.sleep(burst_delay)
            end = time.time()
            print("seq Time: " + str(end-start))
           # after sequence complete save and plot
            if save:
                self.df.to_csv(self.save_file, mode = 'w', index = False)
            # after all data is taken save to sequence csv
            self.fig.canvas.draw()
        return seq_message