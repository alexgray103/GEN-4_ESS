from tkinter import *
import pandas as pd
from tkinter import messagebox

class add_remove_popup:
    def __init__(self, master):
        
        self.master = master
        self.data_headers = None #handles names of headers for plotting
        self.data_headers_idx = None # handles idx of data_headers for selection
        self.ref_selected = None # handles reference selection for ratio_view
        self.ref_ratio_idx = None # idx the ref value for ratio_view
        self.ref_ratio = None
        self.data_pd = None
        
    def create_add_remove(self, save_file):
        self.add_remove = Toplevel(self.master)
        self.add_remove.geometry('370x400')
        self.add_remove.title('Select plot(s) to view')
        self.add_remove.config(bg = "sky blue")
        self.save_file = save_file
        # create frames for 2 different listboxes
        select_frame = Frame(self.add_remove, bg = 'sky blue')
        select_frame.grid(row = 0, column = 0)
        
        # allow buttons and frames to resize with the resizing of the root window
        self.add_remove.grid_columnconfigure(0,weight = 1)
        self.add_remove.grid_rowconfigure(0,weight = 1)
        
        select_frame.grid_rowconfigure((0,1,2,3), weight =1)
        select_frame.grid_columnconfigure((0,1,2,3), weight =1)
        
        #add listbox with scrollbar to select data to be plotted 
        lb = Listbox(select_frame, selectmode = MULTIPLE)
        scrollbar = Scrollbar(select_frame)
        scrollbar.config(command = lb.yview)
        scrollbar.grid(row = 0, column = 3, sticky = N+S+E+W)
        lb.configure(width = 15, height = 10,
                     font=("Times New Roman", 16),
                     yscrollcommand = scrollbar.set,
                     exportselection = False)
        
        lb.grid(row = 0, column = 2, sticky= 'nsew')
        
         #create reference listbox with scroll bar to select reference to be used 
        lb_reference = Listbox(select_frame, selectmode = SINGLE)
        scrollbar_ref =Scrollbar(select_frame)
        scrollbar_ref.config(command = lb_reference.yview)
        scrollbar_ref.grid(row = 0, column = 1, sticky =  N+S+E+W)
        lb_reference.configure(width = 15, height = 10,
                               font=("Times New Roman", 16),
                               yscrollcommand = scrollbar_ref.set,
                               exportselection = False)
        lb_reference.grid(row = 0, column = 0, sticky= 'nsew')
                
        # if there is a save file, then insert scan names
        if self.save_file is not None:
            self.data_pd = pd.read_csv(self.save_file) #handles gettings spectra names
            
            # get col header names to add to listbox text
            data_headers_dummy = list(self.data_pd.columns.values)
            for col in range(1, len(data_headers_dummy),1):
                lb.insert('end', data_headers_dummy[col])
            #select previously selected items
            if self.data_headers_idx is not None:
                for i in self.data_headers_idx:
                    lb.selection_set(i)
                    
            reference_headers = [i for i in data_headers_dummy if i.startswith('Reference')]
            for col in range(0, len(reference_headers),1):
                lb_reference.insert('end', reference_headers[col])
            lb_reference.grid(row = 0, column = 0)
            # select previously selected 
            if self.ref_ratio_idx is not None:
                lb_reference.selection_set(self.ref_ratio_idx)
            else:
                lb_reference.selection_set(END) # select most recent if none is previous
            
        def save_selected():
            
            self.data_headers = [lb.get(idx) for idx in lb.curselection()]
            try:
                self.ref_ratio = lb_reference.get(lb_reference.curselection()) # get reference selected and save name
                self.ref_ratio_idx = lb_reference.curselection()
                
            except:
                self.ref_ratio_idx = None
                self.ref_ratio = None
            # save selected reference to use for ratio conversion
            #check if the data headers is empty to set to none for future plotting 
            try:
                if self.data_headers == []:
                    self.data_headers = None
                    self.data_headers_idx = None 
                else:
                    self.data_headers_idx = lb.curselection()
            
                self.add_remove.destroy()
                
            except:
                self.add_remove.destroy()
            
        def select_all():
            lb.select_set(0, END)
        def unselect_all():
            lb.select_clear(0, END)

        #create selection buttons
        save_selected_button = Button(select_frame, text = 'Save Selected', height = 3, command = save_selected)
        save_selected_button.grid(row = 1, column = 0, columnspan = 4, sticky= 'nsew')
        select_all_button = Button(select_frame, text = 'Select_all',height = 3,   command = select_all)
        select_all_button.grid(row = 2, column = 0, columnspan = 4, sticky= 'nsew')
        Unselect_all_button = Button(select_frame, text = 'Un-Select_all',height = 3,  command = unselect_all)
        Unselect_all_button.grid(row = 3, column = 0, columnspan = 4, sticky= 'nsew')
        