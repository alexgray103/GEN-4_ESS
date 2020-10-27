from tkinter import *
import numpy as np
import os
import pandas as pd

################# Global Variables #################################
exp_folder = []
save_file = []
scan_file = []
wavelength = np.zeros(288)
global filename


class key_pad:
    def __init__(self, master):
        self.keypad = Toplevel(master)
        self.path = '/Users/Alexander/Desktop/'
        big_font = ('Times New Roman', 24)
        self.keypad.title('Input New FileName into entry box')
        #if full_screen == True:
        #self.key_pad.attributes('-fullscreen', True) # fullscreen on touchscreen
        #size = str(self.w-300) + 'x' + str(self.h - 300)
        self.keypad.geometry('680x400')
        
        keypad_frame = Frame(self.keypad)
        keypad_frame.grid(row = 0, column = 0, columnspan = 10, sticky = 'nsew')
        self.key = StringVar()
        key_entry = Entry(keypad_frame, textvariable =self.key, font = big_font, justify = CENTER, )
        key_entry.grid(row = 0, column = 0, sticky = 'nsew')
        self.keypad.grid_columnconfigure((0,1,2,3,4,5,6,7,8,9), weight = 2)
        self.keypad.grid_rowconfigure((1,2,3,4), weight = 2)
        keypad_frame.grid_rowconfigure((0), weight = 1)
        keypad_frame.grid_columnconfigure((0), weight = 1)
    
    def create_keypad(self):
        global filename
        global foldername
        
        def press(letter):
            global current
            current = self.key.get()
            self.key.set('')
            current = str(current) + str(letter)
            self.key.set(current)
        
        def back():
            self.keypad.destroy()
            
        def key_pad_delete():
            global current
            current = current[:-1] # Remove last digit
            self.key.set(current)
        
        def key_pad_save():
            global filename
            global foldername
            path = '/home/pi/Desktop/Spectrometer/'
            filename = str(self.key.get())
            foldername = str(path + self.key.get())
            self.keypad.destroy()
            
        
        btn_list = [
        '1', '2', '3', '4', '5', '6','7', '8', '9', '0',
        'Q', 'W', 'E','R', 'T', 'Y', 'U', 'I', 'O','P',
        'A', 'S', 'D','F', 'G', 'H', 'J', 'K', 'L','bkspce',
        'Z', 'X', 'C','V', 'B', 'N', 'M', '_', 'BACK','OK']
    
        r = 1
        c = 0
        n = 0
    
        btn = list(range(len(btn_list)))
            
        for  label in btn_list:
            btn[n] = Button(self.keypad, text = label, width = 5, height = 4)
            btn[n].grid(row = r, column = c, sticky = 'nsew')
            if n == 29:
                btn[n].configure(command =key_pad_delete)
            elif n== 38:
                btn[n].configure(command =back)
            elif n == 39:
                btn[n].configure(command =key_pad_save)
            else:
                btn[n].configure(command =lambda n = n: press(btn_list[n]))
            n+= 1
            c+= 1
            if c>9:
                c = 0
                r+= 1
         
        '''
        # first row commands
        btn[0].configure(command = lambda: press(1))
        btn[1].configure(command = lambda: press(2))
        btn[2].configure(command = lambda: press(3))
        btn[3].configure(command = lambda: press(4))
        btn[4].configure(command = lambda: press(5))
        btn[5].configure(command = lambda: press(6))
        btn[6].configure(command = lambda: press(7))
        btn[7].configure(command = lambda: press(8))
        btn[8].configure(command = lambda: press(9))
        btn[9].configure(command = lambda: press(0))
        # second row commands
        btn[10].configure(command = lambda: press('q'))
        btn[11].configure(command = lambda: press('w'))
        btn[12].configure(command = lambda: press('e'))
        btn[13].configure(command = lambda: press('r'))
        btn[14].configure(command = lambda: press('t'))
        btn[15].configure(command = lambda: press('y'))
        btn[16].configure(command = lambda: press('u'))
        btn[17].configure(command = lambda: press('i'))
        btn[18].configure(command = lambda: press('o'))
        btn[19].configure(command = lambda: press('p'))
        #third row commands
        btn[20].configure(command = lambda: press('a'))
        btn[21].configure(command = lambda: press('s'))
        btn[22].configure(command = lambda: press('d'))
        btn[23].configure(command = lambda: press('f'))
        btn[24].configure(command = lambda: press('g'))
        btn[25].configure(command = lambda: press('h'))
        btn[26].configure(command = lambda: press('j'))
        btn[27].configure(command = lambda: press('k'))
        btn[28].configure(command = lambda: press('l'))
        btn[29].configure(command = key_pad_delete)

        #fourth row commandxs
        btn[30].configure(command = lambda: press('z'))
        btn[31].configure(command = lambda: press('x'))
        btn[32].configure(command = lambda: press('c'))
        btn[33].configure(command = lambda: press('v'))
        btn[34].configure(command = lambda: press('b'))
        btn[35].configure(command = lambda: press('n'))
        btn[36].configure(command = lambda: press('m'))
        btn[37].configure(command = lambda: press('_'))
        btn[38].configure(command = back)
        btn[39].configure(command = key_pad_save)
        '''
        # wait until window is destroyed then return the filename
        self.keypad.wait_window()
        return (filename, foldername)
        
    