from settings import Settings as _Settings
from number_pad import *
from ESS_functions import *
import csv
import os
import numpy as np

# module connect functionality 
from tkinter import *
import ESS_GUI_module_0
import ESS_GUI_module_1
import ESS_GUI_module_3
import ESS_GUI_module_4
import ESS_GUI_module_5
import ESS_GUI_module_6
import ESS_GUI_module_7



from settings import Settings as _Settings


import serial
import matplotlib.pyplot as plt
from time import sleep

########## global variables ######################
settings_file = '/home/pi/Desktop/Spectrometer/settings/settings.csv'


class settings_popup_window:
    def __init__(self, parent, master):
        global settings_file
        self.master = master
        self.settings_popup = parent
        self.settings_file = settings_file
        self.settings_popup.title('Settings')
        self.settings_popup.configure(bg= "sky blue")
        full_screen = True
        if full_screen == True:
            self.settings_popup.attributes('-fullscreen', True) # Fullscreen on touch screen
        else:
            self.settings_popup.geometry('600x480') # set the size of the monitor
        self.settings_buttons()     # actually create the buttons
        
    def module_connect(self):

        port = "/dev/ttyUSB0"
        port2 = "/dev/ttyUSB1"
        try:
            ser = serial.Serial(port, baudrate = 115200, timeout = 3)
        except:
            ser = serial.Serial(port2, baudrate = 115200, timeout =3)

        sleep(2.5) # wait for a little to initialize serial connection

        ser.write(b'module\n')
        module = int(ser.readline().decode()) # read in the module number
        
        self.master.destroy()
        self.master.quit()
        root = Tk()
        
        if module == 0:
            app = ESS_GUI_module_0.Module_0(root)
            
            
        elif module == 1:
            app = ESS_GUI_module_1.Module_1(root)
            
            
        elif module == 2:
            app = ESS_GUI_module_2.Module_2(root)
            
            
        elif module == 3:
            app = ESS_GUI_module_3.Module_3(root)
            
            
        elif module == 4:
            app = ESS_GUI_module_4.Module_4(root)
            
        elif module == 5:
            app = ESS_GUI_module_5.Module_5(root)
            
        elif module == 6:
            app = ESS_GUI_module_6.Module_6(root)
            
        elif module == 7:
            app = ESS_GUI_module_7.Module_7(root)
        
        
        root.mainloop()
        
            
    def settings_buttons(self):
        myfont = font.Font(size = 9)
        sticky_to = "nsew"
        frame_padding = 5
        settings_button_frame = Frame(self.settings_popup, width = 350, height =120, background = "sky blue")
        #settings_button_frame.place(x = 585, y = 340)
        settings_button_frame.grid(row = 3, column = 2, sticky = sticky_to, padx = 2, pady = 2)
            
        quit_button = Button(settings_button_frame, text = "Back", fg = 'Red', command = self.settings_popup.destroy, width = 9, height = 3)
        quit_button.grid(row = 1, column = 0, sticky = sticky_to)
        
        save_button = Button(settings_button_frame, text = "Save", fg = 'Green', command = self.settings_save, width = 22, height = 3)
        save_button.grid(row = 0, column = 0, columnspan = 3, pady = 2, sticky = sticky_to)
        
        default_button = Button(settings_button_frame, text = "Reset To Default Settings", command = self.default, width = 9, height = 3, wraplength = 85)
        default_button.grid(row = 1, column = 1, sticky = sticky_to)
        
        connect_module_button = Button(settings_button_frame, text = "Connect Module", command = self.module_connect, width = 9, height = 3, wraplength = 85)
        connect_module_button.grid(row = 1, column = 2, sticky = sticky_to)
        
        #read in settings
        settings_open = open(self.settings_file, 'r')
        csv_reader = csv.reader(settings_open, delimiter=',')
        settings = list(csv_reader)
        pulse = int(settings[1][1])
        pulse_rate = int(settings[2][1])
        if pulse == 0:
            integ_time = int(settings[3][1])
        else:
            integ_time = int(120 + (pulse-1)*(1000000/pulse_rate))
            if pulse > 1:
                integ_time = int(integ_time + 1000000/pulse_rate)
                
        dark_subtract = int(settings[4][1])
        lamp_voltage = int(settings[5][1])
        auto_pulse_threshold = int(settings[6][1])
        auto_pulse_max = int(settings[7][1])
        smoothing_half_width = int(settings[8][1])
        min_wavelength = int(settings[9][1])
        max_wavelength = int(settings[10][1])
        average_scans = int(settings[11][1])
        smoothing_used = int(settings[12][1])
        step_resolution = int(settings[13][1])
        grid_size = int(settings[14][1])
        a_0 = str(settings[15][1])
        b_1 = str(settings[16][1])
        b_2 = str(settings[17][1])
        b_3 = str(settings[18][1])
        b_4 = str(settings[19][1])
        b_5 = str(settings[20][1])
        burst_delay_sec = float(settings[21][1])
        burst_number = int(settings[22][1])
        self.measurement_burst = ["" for x in range(burst_number)]
        self.pulse_burst = ["" for x in range(burst_number)]
        
        # try to read bursts settings from the csv, if it is empty it will cause
        # an exception and write default values to those new bursts
        for x in range(0,burst_number):
            try:
                self.measurement_burst[x] = str(settings[23+x][1]) 
                self.pulse_burst[x] =  str(settings[33+x][1]) 
            except:
                self.measurement_burst[x] =  str(5) 
                self.pulse_burst[x] =  str(1) 
        
        # Start to create Frames for settings window
        button_background = "white"
        frame_background = 'white'
        fground = "Black"
        
        # _____________Single Acquisition Frame_________________________________
        single_acquisition_frame = Frame(self.settings_popup, background = frame_background)
        #single_acquisition_frame.place(x = left_side, y = 5)
        single_acquisition_frame.grid(row = 0, rowspan = 2, column = 0, sticky = sticky_to, padx = frame_padding, pady=frame_padding)
        
        single_acquisition_label = Label(single_acquisition_frame, text = "Single Acquisition Settings", fg = fground, bg= frame_background)
        single_acquisition_label.grid(row = 0, column = 0, columnspan = 2, sticky = sticky_to)
        self.acquisition_number = IntVar() 
        self.acquisition_number.set(pulse)
        acq_number_button = Button(single_acquisition_frame, text = "Pulses:", fg = fground, bg = button_background, font = myfont,
                                   command = lambda: self.numpad_popup(self.settings_popup, 1))
        acq_number_button.grid(row = 1, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        acq_number_entry = Entry(single_acquisition_frame, textvariable = self.acquisition_number, justify = CENTER)
        acq_number_entry.grid(row = 1, column = 1, padx = 14, pady = 2, sticky = sticky_to)
        
        self.pulse_rate = IntVar()
        self.pulse_rate.set(pulse_rate)
        pulse_rate_button = Button(single_acquisition_frame, text = "Pulse Rate (Hz):", fg = fground, bg = button_background,
                                   font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 2))
        pulse_rate_button.grid(row = 2, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        pulse_rate_entry = Entry(single_acquisition_frame, textvariable = self.pulse_rate, justify = CENTER)
        pulse_rate_entry.grid(row = 2, column = 1, padx = 14, pady = 2, sticky = sticky_to)
  
        self.integ_time = IntVar()
        self.integ_time.set(integ_time)
        integ_time_button = Button(single_acquisition_frame, text = "Integration Time (usec):", fg = fground, bg = button_background,\
                                   font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 3))
        integ_time_button.grid(row = 3, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        integ_time_entry = Entry(single_acquisition_frame, textvariable = self.integ_time, justify = CENTER)
        integ_time_entry.grid(row = 3, column = 1, padx = 14,pady = 2, sticky = sticky_to)
        
        self.average_scans = IntVar()
        self.average_scans.set(average_scans)
        average_scans_button = Button(single_acquisition_frame, text = "# of Averages:", fg = fground, bg = button_background,\
                                   font = myfont,command = lambda: self.numpad_popup(self.settings_popup, 11))
        average_scans_button.grid(row = 4, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        average_scans_entry = Entry(single_acquisition_frame, textvariable = self.average_scans, justify = CENTER)
        average_scans_entry.grid(row = 4, column = 1, padx = 14, pady = 2, sticky = sticky_to)
        
        self.dark_subtract = IntVar()
        self.dark_subtract.set(dark_subtract)
        dark_subtraction_entry = Checkbutton(single_acquisition_frame, text = "Use Dark Subtraction ", variable = self.dark_subtract)
        dark_subtraction_entry.grid(row = 5, column =0, pady = 2, padx = 2, sticky = sticky_to)
        
        self.smoothing_used = IntVar()
        self.smoothing_used.set(smoothing_used)
        smoothing_entry = Checkbutton(single_acquisition_frame, text = "Smoothing  ", variable = self.smoothing_used)
        smoothing_entry.grid(row = 5, column =1, pady = 2, padx = 14, sticky = sticky_to)
        
        #__________________AutoRange Frame ____________________
        Auto_range_frame = Frame(self.settings_popup, background = frame_background)
        Auto_range_frame.grid(row = 2, column =0, sticky = sticky_to, padx = frame_padding, pady=frame_padding)
        auto_range_label = Label(Auto_range_frame, text = "Auto-Ranging:", fg = fground, bg = frame_background)
        auto_range_label.grid(row = 0, column = 0, columnspan = 2, sticky = sticky_to)
        self.threshold = IntVar()
        self.threshold.set(auto_pulse_threshold)
        autopulse_entry_button = Button(Auto_range_frame, text = "AutoPulse Threshold(counts):", fg = fground, font = myfont,
                                        bg = button_background, command = lambda: self.numpad_popup(self.settings_popup, 6))
        autopulse_entry_button.grid(row = 1, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        autopulse_entry = Entry(Auto_range_frame, textvariable = self.threshold, justify = CENTER)
        autopulse_entry.grid(row = 1, column = 1, padx = 8, sticky = sticky_to)
        
        self.max_pulses = IntVar()
        self.max_pulses.set(auto_pulse_max)
        max_pulses_entry_button = Button(Auto_range_frame, text = "Max # of Pulses:", fg = fground, bg = button_background,
                                         font = myfont,command = lambda: self.numpad_popup(self.settings_popup, 7))
        max_pulses_entry_button.grid(row = 2, column = 0, sticky = sticky_to, padx = 1, pady=1)
        max_pulses_entry = Entry(Auto_range_frame, textvariable = self.max_pulses, justify = CENTER)
        max_pulses_entry.grid(row = 2, column = 1, padx = 8, pady = 4, sticky = sticky_to)
        
        #_________________ Graph settings frame __________________
        graph_frame = Frame(self.settings_popup, width = 340, height = 200, background = frame_background)
        #graph_frame.place(x = left_side, y = 350)
        graph_frame.grid(row = 3, column = 0, sticky = sticky_to, padx = frame_padding, pady=frame_padding)
        
        graph_frame_label = Label(graph_frame, text = "Graphing Options:", fg = fground, bg = frame_background)
        graph_frame_label.grid(row = 0, column = 0, columnspan = 2, sticky = sticky_to)
        self.smoothing = IntVar()
        self.smoothing.set(smoothing_half_width)
        smoothing_entry_button = Button(graph_frame, text = "Smoothing Half-Width (pixels):", fg = fground, bg = button_background,
                                        font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 8), state = DISABLED)
        smoothing_entry_button.grid(row = 1, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        smoothing_entry = Entry(graph_frame, textvariable = self.smoothing, justify = CENTER, state = DISABLED)
        smoothing_entry.grid(row = 1, column = 1, padx = 8, sticky = sticky_to)
        
        self.min_wavelength = IntVar()
        self.min_wavelength.set(min_wavelength)
        min_wavelength_entry_button = Button(graph_frame, text = "Min-Wavelength:", fg = fground, bg = button_background,
                                             font = myfont,command = lambda: self.numpad_popup(self.settings_popup, 9))
        min_wavelength_entry_button.grid(row = 2, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        min_wavelength_entry = Entry(graph_frame, textvariable = self.min_wavelength, justify = CENTER)
        min_wavelength_entry.grid(row = 2, column = 1, padx = 8, sticky = sticky_to)
        
        self.max_wavelength = IntVar()
        self.max_wavelength.set(max_wavelength)
        max_wavelength_entry_button = Button(graph_frame, text = "Max-Wavelength:", fg = fground, bg = button_background,
                                             font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 10))
        max_wavelength_entry_button.grid(row = 3, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        max_wavelength_entry = Entry(graph_frame, textvariable = self.max_wavelength, justify = CENTER)
        max_wavelength_entry.grid(row = 3, column = 1, padx = 8, sticky = sticky_to)
        
        #_________calibration Coefficients frame ______________________
        wavelength_pixel_frame = Frame(self.settings_popup, width = 340, height =120, background = frame_background)
        #wavelength_pixel_frame.place(x = 325, y = 245)
        wavelength_pixel_frame.grid(row = 2, column = 1, sticky = sticky_to, padx = frame_padding, pady=frame_padding, rowspan = 2)
        wavelength_pixel_label = Label(wavelength_pixel_frame, text = "Calibration Coefficients", fg = fground, bg= frame_background, justify = CENTER)
        wavelength_pixel_label.grid(row = 0, column = 0, columnspan = 3, sticky = sticky_to)
        self.a_0 = StringVar()
        self.a_0.set(a_0)
        a0_button = Button(wavelength_pixel_frame, text = "A_0: ", fg = fground, bg = button_background,
                           font = myfont,command = lambda: self.numpad_popup(self.settings_popup, 15))
        a0_button.grid(row = 1, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        a0_entry = Entry(wavelength_pixel_frame, textvariable = self.a_0, width = 16)
        a0_entry.grid(row = 1, column = 1, padx = 8, sticky = sticky_to)
        
        self.b_1 = StringVar()
        self.b_1.set(b_1)
        b1_button = Button(wavelength_pixel_frame, text = "B_1: ", fg = fground, bg = button_background,
                           font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 16))
        b1_button.grid(row = 2, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        b1_entry = Entry(wavelength_pixel_frame, textvariable = self.b_1, width = 16)
        b1_entry.grid(row = 2, column = 1, padx = 8, sticky = sticky_to)
        
        self.b_2 = StringVar()
        self.b_2.set(b_2)
        b2_button = Button(wavelength_pixel_frame, text = "B_2: ", fg = fground, bg = button_background,
                           font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 17))
        b2_button.grid(row = 3, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        b2_entry = Entry(wavelength_pixel_frame, textvariable = self.b_2, width = 16)
        b2_entry.grid(row = 3, column = 1, padx = 8, sticky = sticky_to)
        b2_exp_label = Label(wavelength_pixel_frame, text = "e-03", fg = fground, bg= "white", justify = CENTER)
        b2_exp_label.grid(row = 3, column = 2,  sticky = sticky_to)
        
        self.b_3 = StringVar()
        self.b_3.set(b_3)
        b3_button = Button(wavelength_pixel_frame, text = "B_3: ", fg = fground, bg = button_background,
                           font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 18))
        b3_button.grid(row = 4, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        b3_entry = Entry(wavelength_pixel_frame, textvariable = self.b_3, width = 16)
        b3_entry.grid(row = 4, column = 1, padx = 8, sticky = sticky_to)
        b3_exp_label = Label(wavelength_pixel_frame, text = "e-06", fg = fground, bg= "white", justify = CENTER)
        b3_exp_label.grid(row = 4, column = 2,  sticky = sticky_to)
        
        self.b_4 = StringVar()
        self.b_4.set(b_4)
        b4_button = Button(wavelength_pixel_frame, text = "B_4: ", fg = fground, bg = button_background,
                           font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 19))
        b4_button.grid(row = 5, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        b4_entry = Entry(wavelength_pixel_frame, textvariable = self.b_4, width = 16)
        b4_entry.grid(row = 5, column = 1, padx = 8, sticky = sticky_to)
        b4_exp_label = Label(wavelength_pixel_frame, text = "e-09", fg = fground, bg= "white", justify = CENTER)
        b4_exp_label.grid(row = 5, column = 2, sticky = sticky_to)
        
        self.b_5 = StringVar()
        self.b_5.set(b_5)
        b5_button = Button(wavelength_pixel_frame, text = "B_5: ", fg = fground, bg = button_background,
                           font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 20))
        b5_button.grid(row = 6, column = 0, pady = 2, padx = 3, sticky = sticky_to)
        b5_entry = Entry(wavelength_pixel_frame, textvariable = self.b_5, width = 16)
        b5_entry.grid(row = 6, column = 1, padx = 8, sticky = sticky_to)
        b5_exp_label = Label(wavelength_pixel_frame, text = "e-12", fg = fground, bg= "white", justify = CENTER)
        b5_exp_label.grid(row = 6, column = 2, sticky = sticky_to)
        
        #_______Stepper frame_______________
        stepper_frame = Frame(self.settings_popup, width = 340, height =120, background = frame_background)
        stepper_frame.grid(row = 1, column = 1, sticky = sticky_to, padx = frame_padding, pady=frame_padding)
        stepper_label = Label(stepper_frame, text = "Scan Settings",fg = fground, bg = frame_background)
        stepper_label.grid(row = 0, column = 0, columnspan = 2, sticky = sticky_to)
        
        self.step_size = IntVar()
        self.step_size.set(step_resolution)
        step_size_button = Button(stepper_frame, text = "Step Size (um)", fg = 'black', bg = button_background,
                                  font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 13))
        step_size_button.grid(row = 1, column = 0, padx = 3, pady = 3, sticky = sticky_to)
        step_size_entry = Entry(stepper_frame, textvariable = self.step_size, justify = CENTER)
        step_size_entry.grid(row = 1, column = 1, padx = 8, sticky = sticky_to)
        
        self.grid_size = IntVar()
        self.grid_size.set(grid_size)
        grid_size_button = Button(stepper_frame, text = "Grid Size", fg = 'black', bg = button_background,
                                  font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 14))
        grid_size_button.grid(row = 2, column = 0, padx = 3, pady = 3, sticky = sticky_to)
        grid_size_entry = Entry(stepper_frame, textvariable = self.grid_size, justify = CENTER)
        grid_size_entry.grid(row = 2, column = 1, padx = 8, sticky = sticky_to)
        
        #___________ sequence Frame _______________________
        sequence_frame = Frame(self.settings_popup, width = 340, height =120, background = frame_background)
        #sequence_frame.place(x = 325, y = 5)
        sequence_frame.grid(row = 0, column = 1, sticky = sticky_to, padx = frame_padding, pady=frame_padding)
        sequence_label = Label(sequence_frame, text = "Sequence Settings",fg = fground, bg = frame_background)
        sequence_label.grid(row = 0, column = 0, columnspan = 2, sticky = sticky_to)
        
        self.burst_number = IntVar()
        self.burst_number.set(burst_number)
        burst_number_button = Button(sequence_frame, text = "# of Bursts: ", fg = 'black', bg = button_background,
                                     font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 22))
        burst_number_button.grid(row = 1, column = 0, padx = 3, pady = 10, sticky = sticky_to)
        burst_number_entry = Entry(sequence_frame, textvariable = self.burst_number, justify = CENTER)
        burst_number_entry.grid(row = 1, column = 1, padx = 8, pady = 10, sticky = sticky_to)
        
        self.burst_delay_number = StringVar()
        self.burst_delay_number.set(burst_delay_sec)
        burst_delay_button = Button(sequence_frame, text = "Interburst delay: ", fg = 'black', bg = button_background,
                                    font = myfont, command = lambda: self.numpad_popup(self.settings_popup, 21))
        burst_delay_button.grid(row = 2, column = 0, padx = 3, pady = 10, sticky = sticky_to)
        burst_delay_entry = Entry(sequence_frame, textvariable = self.burst_delay_number, justify = CENTER)
        burst_delay_entry.grid(row = 2, column = 1, padx = 8,pady = 10, sticky = sticky_to)
        
        #___________burst Frame ______________
        label_font = font.Font(size=6)
        self.burst_frame = Frame(self.settings_popup, width = 340, height =120, background = frame_background)
        self.burst_frame.grid(row = 0, column = 2, sticky = sticky_to, padx = frame_padding, pady=frame_padding, rowspan = 3)
        number_measurements_burst_label = Label(self.burst_frame, justify = CENTER, wraplength = 60, text = "# Measurements",
                                                font = label_font, fg = fground, bg = button_background,borderwidth=1, relief="solid")
        number_measurements_burst_label.grid(row = 0, column = 0, padx = 4, pady = 3, sticky = sticky_to)
        pulses_per_burst_label = Label(self.burst_frame,justify = CENTER, wraplength = 60, text = "Pulses per Measurement",
                                       font = label_font, fg = fground, bg = button_background, borderwidth=1, relief="solid")
        pulses_per_burst_label.grid(row = 0, column = 1, padx = 4, pady = 3, sticky = sticky_to)
        
        #create x number of buttons depending on number of bursts provided
        #limited to 10 bursts for spacing reasons
        for x in range(0,burst_number):
            self.measurement_burst_button = Button(self.burst_frame, text = self.measurement_burst[x], fg = 'black', bg = button_background,
                                                   command = lambda x =x: self.numpad_popup(self.settings_popup, 23+x), font = myfont)
            self.measurement_burst_button.grid(row = 1+x, column = 0, padx = 3, pady = 1, sticky = sticky_to)
        
            self.pulse_burst_button= Button(self.burst_frame, text = self.pulse_burst[x], fg = 'black', bg = button_background,
                                            command = lambda x =x: self.numpad_popup(self.settings_popup, 33+x), font = myfont)
            self.pulse_burst_button.grid(row = 1+x, column = 1, padx = 3, pady = 1, sticky = sticky_to)
            
        # resizable buttons and frames within this window
        self.settings_popup.grid_columnconfigure((0,1,2),weight = 1)
        self.settings_popup.grid_rowconfigure((0,1,2),weight = 1)
        single_acquisition_frame.grid_columnconfigure((0,1),weight = 1)
        single_acquisition_frame.grid_rowconfigure((0,1,2,3,4,5),weight = 1)
        #lamp.grid_columnconfigure((0,1,2,3,4,5,6),weight = 1)
        #lamp.grid_rowconfigure((0,1,2,3,4,5,6),weight = 1)
        Auto_range_frame.grid_columnconfigure((0,1),weight = 1)
        Auto_range_frame.grid_rowconfigure((0,1,2),weight = 1)
        graph_frame.grid_columnconfigure((0,1),weight = 1)
        graph_frame.grid_rowconfigure((0,1,2,3),weight = 1)
        wavelength_pixel_frame.grid_columnconfigure((0,1,2),weight = 1)
        wavelength_pixel_frame.grid_rowconfigure((0,1,2,3,4,5,6),weight = 1)
        stepper_frame.grid_columnconfigure((0,1),weight = 1)
        stepper_frame.grid_rowconfigure((0,1,2),weight = 1)
        sequence_frame.grid_columnconfigure((0,1),weight = 1)
        sequence_frame.grid_rowconfigure((0,1,2),weight = 1)
        self.burst_frame.grid_columnconfigure((0,1),weight = 1)
        self.burst_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10),weight = 1)
        settings_button_frame.grid_columnconfigure((0,1),weight = 1)
        settings_button_frame.grid_rowconfigure((0,1),weight = 1)
        
    def settings_save(self):
        settings_open = open(self.settings_file, 'r')
        csv_reader = csv.reader(settings_open, delimiter=',')
        settings = list(csv_reader)
        # get all values from the entry boxes and save to settings CSV file
        settings[1][1]  = int(self.acquisition_number.get())
        settings[2][1] = int(self.pulse_rate.get())
        settings[3][1] = int(self.integ_time.get())
        settings[4][1] = int(self.dark_subtract.get())
        #settings[5][1] = int(self.lamp_voltage.get())
        settings[6][1] = int(self.threshold.get())
        settings[7][1]= int(self.max_pulses.get())
        settings[8][1] = int(self.smoothing.get())
        settings[9][1] = int(self.min_wavelength.get())
        settings[10][1] = int(self.max_wavelength.get())
        settings[11][1] = int(self.average_scans.get())
        settings[12][1] = int(self.smoothing_used.get())
        settings[13][1] = int(self.step_size.get())
        settings[14][1] = int(self.grid_size.get())
        settings[15][1] = float(self.a_0.get())
        settings[16][1] = float(self.b_1.get())
        settings[17][1] = float(self.b_2.get())
        settings[18][1] = float(self.b_3.get())
        settings[19][1] = float(self.b_4.get())
        settings[20][1] = float(self.b_5.get())
        settings[21][1] = float(self.burst_delay_number.get())
        settings[22][1] = int(self.burst_number.get())
        
        for x in range(0,settings[22][1]):
            settings[23+x][1] = int(self.measurement_burst[x])
            settings[33+x][1] = int(self.pulse_burst[x])
        
        #save_settings_var() # save settings to main class attributes   
        settings_open = open(self.settings_file, 'w')
        with settings_open:
           csv_writer = csv.writer(settings_open, delimiter = ',')
           csv_writer.writerows(settings)
        A = float(settings[15][1])
        B1 = float(settings[16][1])
        B2 = float(settings[17][1])/1000
        B3 = float(settings[18][1])/1000000
        B4 = float(settings[19][1])/1000000000
        B5 = float(settings[20][1])/1000000000000
        
        global wavelength
        #initialize wavelength array with zeros then solve given pixel coefficients
        wavelength = np.zeros(288)
        for pixel in range(1,289,1):
            wavelength[pixel-1] = A + B1*pixel + B2*(pixel**2) + B3*(pixel**3) + B4*(pixel**4) + B5*(pixel**5)
        self.settings_popup.destroy()
        
    def default(self):
        self.acquisition_number.set('1')
        self.pulse_rate.set('60')
        self.integ_time.set('120')
        self.dark_subtract.set('1')
        #self.lamp_voltage.set('1000')
        self.threshold.set('60000')
        self.smoothing.set('3')
        self.min_wavelength.set('300')
        self.max_wavelength.set('900')
        self.average_scans.set('1')
        self.smoothing_used.set('1')
        self.step_size.set('500')
        self.grid_size.set('10')
        self.a_0.set('306.2701737')
        self.b_1.set('2.712800137')
        self.b_2.set('-1.301585429')
        self.b_3.set('-5.886856881')
        self.b_4.set('17.33842519')
        self.b_5.set('15.99830646')
        self.burst_delay_number.set('1.0')
        self.burst_number.set('1')
        self.measurement_burst = str(5)
        self.pulse_burst = str(1) 
        
        #reset Bursts buttons 
        sticky_to = "nsew"
        self.measurement_burst_button = Button(self.burst_frame, text = self.measurement_burst, fg = 'black', bg = "white", command = lambda: self.numpad_popup(self.settings_popup, 23))
        self.measurement_burst_button.grid(row = 2, column = 0, padx = 3, pady = 3, sticky = sticky_to)
        
        self.pulse_burst_button= Button(self.burst_frame, text = self.pulse_burst, fg = 'black', bg = "white", command = lambda: self.numpad_popup(self.settings_popup, 24))
        self.pulse_burst_button.grid(row = 2, column = 1, padx = 3, pady = 3, sticky = sticky_to)
        
        settings_open = open(self.settings_file, 'r')
        csv_reader = csv.reader(settings_open, delimiter=',')
        settings = list(csv_reader)
        settings[1][1]  = int(self.acquisition_number.get())
        settings[2][1] = int(self.pulse_rate.get())
        settings[3][1] = int(self.integ_time.get())
        settings[4][1] = int(self.dark_subtract.get())
        #settings[5][1] = int(self.lamp_voltage.get())
        settings[6][1] = int(self.threshold.get())
        settings[7][1]= int(self.max_pulses.get())
        settings[8][1] = int(self.smoothing.get())
        settings[9][1] = int(self.min_wavelength.get())
        settings[10][1] = int(self.max_wavelength.get())
        settings[11][1] = int(self.average_scans.get())
        settings[12][1] = int(self.smoothing_used.get())
        settings[13][1] = int(self.step_size.get())
        settings[14][1] = int(self.grid_size.get())
        settings[15][1] = float(self.a_0.get())
        settings[16][1] = float(self.b_1.get())
        settings[17][1] = float(self.b_2.get())
        settings[18][1] = float(self.b_3.get())
        settings[19][1] = float(self.b_4.get())
        settings[20][1] = float(self.b_5.get())
        settings[21][1] = float(self.burst_delay_number.get())
        settings[22][1] = int(self.burst_number.get())
        settings[23][1] = int(self.measurement_burst)
        settings[33][1] = int(self.pulse_burst)
        
        # write settings array to csv 
        settings_open = open(self.settings_file, 'w')
        with settings_open:
            csv_writer = csv.writer(settings_open, delimiter = ',')
            csv_writer.writerows(settings)
        # reset the window
        self.window_refresh()
        
    def numpad_popup(self, parent, number):
        self.popup = Toplevel(parent)
        self.numpad = Num_Pad(self.popup, number)
        parent.wait_window(self.popup)
        self.window_refresh()
        
    def window_refresh(self):
        self.settings_popup.destroy()
        self.settings_wind = Toplevel(self.master)
        self.sett_popup = settings_popup_window(self.settings_wind, self.master)

    