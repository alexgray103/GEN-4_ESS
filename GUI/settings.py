import csv
import numpy as np


class Settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        
    def create_settings(self):
        open(self.settings_file, 'x')
        settings_open = open(self.settings_file, 'w', newline = '')
        csv_row = [('Settings', ''),('pulse',1),('pulse_rate',60),\
            ('integration_time',300),('dark_subtract',1),\
            ('lamp_voltage',1000), ('autopulse_threshold',60000),\
            ('max_autopulse_number',10),('smoothing_half_width',2),\
            ('min_wavelength',300),('max_wavelength',900),\
            ('Number_of_Averages', 2), ('smoothing', 1),\
            ('Grid Size', 10), ('Step Size', 500),\
            ('a_0', 308.6578728), ('b_1', 2.71512091),\
            ('b_2', -1.581742352), ('b_3', -3.64516878),\
            ('b_4', -6.471720765), ('b_5', 27.41135617),\
            ('burst_delay', 1.0), ('burst_number', 1),\
            ('measurement_per_burst_1', 5),('measurement_per_burst_2', 5),\
            ('measurement_per_burst_3', 5),('measurement_per_burst_4', 5),\
            ('measurement_per_burst_5', 5),('measurement_per_burst_6', 5),\
            ('measurement_per_burst_7', 5),('measurement_per_burst_8', 5),\
            ('measurement_per_burst_9', 5),('measurement_per_burst_10', 5),\
            ('pulse_per_measurement_1', 1),('pulse_per_measurement_2', 1),\
            ('pulse_per_measurement_3', 1),('pulse_per_measurement_4', 1),\
            ('pulse_per_measurement_5', 1),('pulse_per_measurement_6', 1),\
            ('pulse_per_measurement_7', 1),('pulse_per_measurement_8', 1),\
            ('pulse_per_measurement_9', 1),('pulse_per_measurement_10', 1)]   # allocate 10 spaces for burst info
            
        with settings_open:
            csv_writer = csv.writer(settings_open, delimiter = ',')
            csv_writer.writerows(csv_row)
                
    def settings_read(self):
        settings_open = open(self.settings_file, 'r')
        csv_reader = csv.reader(settings_open, delimiter=',')
        settings = list(csv_reader)
        
        A = float(settings[15][1])
        B1 = float(settings[16][1])
        B2 = float(settings[17][1])/1000
        B3 = float(settings[18][1])/1000000
        B4 = float(settings[19][1])/1000000000
        B5 = float(settings[20][1])/1000000000000

        #initialize wavelength array with zeros then solve given pixel coefficients
        wavelength = np.zeros(288)
        for pixel in range(1,289,1):
            wavelength[pixel-1] = A + B1*pixel + B2*(pixel**2) + B3*(pixel**3) + B4*(pixel**4) + B5*(pixel**5)
        return (settings, wavelength)
    
    def settings_write(self, settings_array):
        settings_open = open(self.settings_file, 'w')
        with settings_open:
            csv_writer = csv.writer(settings_open, delimiter = ',')
            csv_writer.writerows(settings_array)
