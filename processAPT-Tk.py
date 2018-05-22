# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 10:42:18 2018

@author: jfarrugia
"""

import tkinter as tk
from tkinter import messagebox
import datetime as dt
from tkinter import filedialog
import pandas as pd
np = pd.np

# VERSIONS
# v1.1 - added surpport for raw data archiving with three timestamp columns
# v1.2 - added support for sample rate specification for archive

class APT_Calibration:
    
    def __init__(self, master):
        # first frame will contain the browse field
        self.browse_frame = tk.Frame(root)
        self.browse_frame.pack()
        tk.Label(self.browse_frame, text = 'Select files: ').grid(row=4, column=0, sticky = 'e')
        
        # Browse button
        self.bbutton= tk.Button(self.browse_frame, text="Browse", command=self.browseFiles)
        self.bbutton.grid(row=4, column=1, sticky='w')
        self.opt_var = tk.StringVar(root)
        
        tk.Label(self.browse_frame, text = 'Optional archive: ').grid(row=1, column=0, sticky='e')
        #Optional archive option
        self.opt_var.set("Choose a Processing Option")
        self.opt_archive = tk.OptionMenu(self.browse_frame, self.opt_var,
                                         "Calibrate",
                                         "Archive") #archives the original raw data files with the three timestamp columns
        self.opt_archive.grid(row=1, column=1, columnspan=2, sticky='w')
        
        #sample rate
        tk.Label(self.browse_frame, text = 'Sample rate: ').grid(row=2, column=0, sticky='e')
        self.e_var = tk.StringVar()
        self.e_var.set("5")
        self.e_samplerate = tk.Entry(self.browse_frame, textvariable=self.e_var)
        self.e_samplerate.grid(row=2, column=1, columnspan=2, sticky='w')
        
        #serial number
        tk.Label(self.browse_frame, text = 'Instrument S/N: ').grid(row=3, column=0, sticky='e')
        self.sn_var = tk.StringVar()
        self.sn_var.set("63055")
        self.e_sn = tk.Entry(self.browse_frame, textvariable=self.sn_var)
        self.e_sn.grid(row=3, column=1, columnspan=2, sticky='w')
        

    def t1t2_to_strings(self, t1, t2):
        d1 = dt.datetime(year=int(t1[:4]), 
                         month=int(t1[5:7]), 
                         day=int(t1[8:10]), 
                         hour=int(t1[11:13]), 
                         minute=int(t1[14:16]), 
                         second=int(t1[17:19])).strftime('%Y%m%d-%H%M%S')
        d2 = dt.datetime(year=int(t2[:4]), 
                         month=int(t2[5:7]), 
                         day=int(t2[8:10]), 
                         hour=int(t2[11:13]), 
                         minute=int(t2[14:16]), 
                         second=int(t2[17:19])).strftime('%Y%m%d-%H%M%S')
        
        return d1, d2     
    
    def browseFiles(self):
        global filenames
        #disables the browsing frame
        for child in self.browse_frame.winfo_children():
            child.configure(state='disable')
        
        filenames = filedialog.askopenfilenames(title = 'Select file(s) to calibrate.')
        
        #pack the second frame
        self.output_frame = tk.Frame(root) 
        self.output_frame.pack()
        self.output_text = tk.Text(self.output_frame, height=15)
        self.to_process_label = tk.Label(self.output_frame, text = 'Paths to files to be processed: ')
        self.to_process_label.grid(row=0, column=0, sticky = 'nw', padx=10, pady=10)
        self.output_text.grid(row=1, column=0)
        
        # scroll bar for output frame widget
        self.scrollb = tk.Scrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollb.grid(row=1, column=1, sticky='nsew')
        self.output_text['yscrollcommand'] = self.scrollb.set
        for i in filenames:
            self.output_text.insert(tk.INSERT, i + '\n')
        self.pbutton = tk.Button(self.output_frame, text = 'Press to process APT data', command = self.processChoice) # press to process
        self.pbutton.grid(row=2, column=0, sticky = 'nsew')
        
    def processChoice(self):
        if self.opt_var.get() == 'Calibrate':
            self.performCalibration()
        elif self.opt_var.get() == 'Archive':
            self.performArchive()
        else:
            messagebox.showwarning("Invalid Selection", "Choose either 'Calibrate' or 'Archive' from the list of processing options.")
            self.opt_archive.configure(state='active')
            
    def performArchive(self):
        # remove button
        self.pbutton.configure(state='disable')
        # Destination for calibrated files
        global output_path
        output_path = filedialog.askdirectory(title = 'Choose a destination for archived file(s).')
        
        # create the third frame to write file names that have been calibrated
        self.writing_frame = tk.Frame(root)
        self.writing_frame.pack()
        self.processed_label = tk.Label(self.writing_frame, text = 'Archived APT files: ')
        self.processed_label.grid(row=0, column=0, sticky = 'nw', padx=10, pady=10)
        self.writing_text = tk.Text(self.writing_frame, height=15)
        self.writing_text.grid(row=1, column=0)
        
        #scroll bar
        self.scrollb_2 = tk.Scrollbar(self.writing_frame, command=self.writing_text.yview)
        self.scrollb_2.grid(row=1, column=1, sticky='nsew')
        self.writing_text['yscrollcommand'] = self.scrollb_2.set
        
        def reformat_raw_files(filename):
            """ Here we just want to add the corrected logger times, and name 
            the first timestamp column appropriately; retain and output raw
            period counts."""
            df = pd.read_csv(filename, 
                             comment ='#',
                             float_precision='high', 
                             sep=',', 
                             header=None, 
                             usecols=['t_logger_ntpsync',
                                      't_logger',
                                      'cx',
                                      'cy',
                                      'cz',
                                      'cTa',
                                      'cP',
                                      'cTP'],
                             names=['t_logger_ntpsync',
                                    't_logger',
                                    'cx',
                                    'cy',
                                    'cz',
                                    'cTa',
                                    'cP',
                                    'cTP'],
                             index_col='t_logger', 
                             infer_datetime_format = True, 
                             parse_dates = True)
            
            #calibrated logger times
            if self.sn_var.get() == 63055:
                flag = 1
                ic_slope = 0.05557783859425694 
                yint = 0.7718555619275425
                dateOfInstall = dt.datetime(2017, 6, 14)
                logger_times = df.index.to_pydatetime()
                cor_times_ = [(t_log - dateOfInstall).total_seconds() + (t_log - dateOfInstall).total_seconds()/60/60/24 * ic_slope + yint for t_log in logger_times] #corrected logger times
                cor_times = [dateOfInstall + dt.timedelta(0, t_cor, 0) for t_cor in cor_times_]
                df['t_log_corr'] = cor_times
                df['_t_logger'] = df.index
                df.index = df['t_logger_ntpsync']
                if logger_times[0] > dt.datetime(2018, 4, 20) or logger_times[0] < dt.datetime(2018, 4, 20) and logger_times[1000] > dt.datetime(2018, 4, 20):
                    pass
                else:
                    df.index.name = 't_ntp'
            else:
                flag = 0
                df['_t_logger'] = df.index
                df.index = df['t_logger_ntpsync']
            
            return df, flag

        #export function
        def exportAPT_archive(out_filename, flag):
            if flag: cols = ['t_log_corr', '_t_logger', 'cx', 'cy', 'cz', 'cTa', 'cP', 'cTP']
            # if not 63055 don't need the corrected logger time
            else: cols = ['_t_logger', 'cx', 'cy', 'cz', 'cTa', 'cP', 'cTP']
            df.to_csv(output_path + '/' + out_filename, columns = cols)
                
            
        for ind, i in enumerate(filenames):
            print('Working on {}/{}.'.format(ind+1, len(filenames)))
            df, flag = reformat_raw_files(i)
            t1 = df.index[0]
            t2 = df.index[-1]
            d1, d2 = self.t1t2_to_strings(t1, t2)
            exportAPT_archive('{}_{}_{}sps_archive.acc'.format(d1, d2, self.e_var.get()), flag)
            self.writing_text.insert(tk.INSERT, output_path + '/' + '{}_{}_{}sps_archive.acc'.format(d1, d2,self.e_var.get()) + '\n')
            self.writing_text.update()
            if i == filenames[-1]:
                messagebox.showinfo("Message", "Job complete!")
            
    def performCalibration(self):
        """ This is where the magic happens. """
        # remove button
        self.pbutton.configure(state='disable')
        # Destination for calibrated files
        global output_path
        output_path = filedialog.askdirectory(title = 'Choose a destination for calibrated file(s).')
        
#        # open file for azimuths and dips
#        dip_azimuth_file = open(output_path + '/' + 'dip_azimuth.txt','a+')
#        dip_azimuth_file.write('Date,Estimated Azimuth (deg),Estimated Dip (deg)\n')
        
        # create the third frame to write file names that have been calibrated
        self.writing_frame = tk.Frame(root)
        self.writing_frame.pack()
        self.processed_label = tk.Label(self.writing_frame, text = 'Calibrated APT files: ')
        self.processed_label.grid(row=0, column=0, sticky = 'nw', padx=10, pady=10)
        self.writing_text = tk.Text(self.writing_frame, height=15)
        self.writing_text.grid(row=1, column=0)
        
        #scroll bar
        self.scrollb_2 = tk.Scrollbar(self.writing_frame, command=self.writing_text.yview)
        self.scrollb_2.grid(row=1, column=1, sticky='nsew')
        self.writing_text['yscrollcommand'] = self.scrollb_2.set
        
        # read in calibration files
        coeffs_acceleration=pd.read_csv('RBR{}_acc_coeffs.dat'.format(self.sn_var.get()),index_col='Serial', comment = '#', 
                       skipinitialspace=True, 
                       float_precision='high').to_dict(orient='index')
        acceleration_serials = list(coeffs_acceleration.keys())
        
        coeffs_pressure=pd.read_csv('RBR{}_pressure_coeffs.dat'.format(self.sn_var.get()),index_col='Serial', comment = '#', 
                           skipinitialspace=True, 
                           float_precision='high').to_dict(orient='index')
        pressure_serials = list(coeffs_pressure.keys())
        
        # alignment matrix for calibrating acceleration data
        #Alignment matrix
        aa = np.loadtxt('RBR{}_alignment_matrix.dat'.format(self.sn_var.get()), comments='#')
        alignMatrix = np.array([[aa[0], aa[1], aa[2]],
                                [aa[3], aa[4], aa[5]],
                                [aa[6], aa[7], aa[8]]])
        
        # Calibration function for APT data (not alignment, or azimuthal rotation)
        def calcCalibration(comp, t, X, scale = 1e-6, unit = 'mps'):
            """ Calculates acceleration [m/s] as well as Pressure [decibars]. Acceleration is calculated using acceleration (t) and temperature 
            (X) period, """
            Units={'mps' : 1, #default
                   'kPa' : 6.89475728, #to convert from psi to kPa
                   'decibar' : 0.689475728} #to convert from psi to decibar
            try:
                if comp == 'X':
                    Ca = coeffs_acceleration[acceleration_serials[0]] #Serial number of each sensor component
                elif comp == 'Y':
                    Ca = coeffs_acceleration[acceleration_serials[1]]
                elif comp == 'Z':
                    Ca = coeffs_acceleration[acceleration_serials[2]]
                elif comp == 'P':
                    Ca = coeffs_pressure[pressure_serials[0]]
            except:
                raise NameError('Invalid selection for "comp". Choose from either "X", "Y", or "Z" to process accelerogram components, or "P" for pressure data.')
                
            #Need a scale to convert from usec to sec
            U = np.float64(X*scale)-Ca['U0']
            Temp = Ca['Y1']*U + Ca['Y2']*U**2
            t0 = Ca['T1'] + Ca['T2']*U + Ca['T3']*U**2 + Ca['T4']*U**3 + Ca['T5']*U**4
            C = Ca['C1'] + Ca['C2']*U + Ca['C3']*U**2
            D = Ca['D1'] + Ca['D2']*U
            E = 1 - t0**2/(np.float64(t*scale))**2
            return [C*E*(1 - D*E)*Units[unit], Temp] #acceleration in m/s, pressure in decibar

        # Apply the calibration function and perform alignment on acceleration data
        def signalProcessVis(filename):
            """ Apply the calibration to acceleration and pressure data, as well as perform alignment on acceleration data. """
            df = pd.read_csv(filename, 
                             comment ='#',
                             float_precision='high', 
                             sep=',', 
                             header=None, 
                             usecols=['t_logger_ntpsync',
                                      't_logger',
                                      'cx',
                                      'cy',
                                      'cz',
                                      'cTa',
                                      'cP',
                                      'cTP'],
                             names=['t_logger_ntpsync',
                                    't_logger',
                                    'cx',
                                    'cy',
                                    'cz',
                                    'cTa',
                                    'cP',
                                    'cTP'],
                             index_col='t_logger', 
                             infer_datetime_format = True, 
                             parse_dates = True)
            # Calculating acceleration [m/s]
            df['acc_X'], df['X_temp'] = calcCalibration('X', df['cx'], df['cTa'])
            df['acc_Y'], df['Y_temp'] = calcCalibration('Y', df['cy'], df['cTa'])
            df['acc_Z'], df['Z_temp'] = calcCalibration('Z', df['cz'], df['cTa'])
            df['P'], df['P_temp'] = calcCalibration('P', df['cP'], df['cTP'], unit = 'decibar')
            
            # Apply sensor alignment
            df['ax'], df['ay'], df['az']  = np.dot(alignMatrix, np.float64([df['acc_X'], df['acc_Y'], df['acc_Z']]))
            
            #calibrated logger times
            if self.sn_var.get() == 63055:
                flag = 1
                ic_slope = 0.05557783859425694 
                yint = 0.7718555619275425
                dateOfInstall = dt.datetime(2017, 6, 14)
                logger_times = df.index.to_pydatetime()
                cor_times_ = [(t_log - dateOfInstall).total_seconds() + (t_log - dateOfInstall).total_seconds()/60/60/24 * ic_slope + yint for t_log in logger_times] #corrected logger times
                cor_times = [dateOfInstall + dt.timedelta(0, t_cor, 0) for t_cor in cor_times_]
                df['t_log_corr'] = cor_times
                df['_t_logger'] = df.index
                df.index = df['t_logger_ntpsync']
                if logger_times[0] > dt.datetime(2018, 4, 20) or logger_times[0] < dt.datetime(2018, 4, 20) and logger_times[1000] > dt.datetime(2018, 4, 20):
                    pass
                else:
                    df.index.name = 't_ntp'
            else:
                flag = 0
                df['_t_logger'] = df.index
                df.index = df['t_logger_ntpsync']
                
            return df, flag
        
        #export function
        def exportAPT(out_filename, flag):
            if flag: cols = ['t_log_corr','_t_logger', 'ax', 'ay', 'az', 'P', 'P_temp', 'Z_temp']
            # if not 63055 don't need the corrected logger time
            else: cols = ['_t_logger', 'ax', 'ay', 'az', 'P', 'P_temp', 'Z_temp']
            df.to_csv(output_path + '/' + out_filename, columns = cols)
                

        for ind, i in enumerate(filenames):
            print('Working on {}/{}.'.format(ind+1, len(filenames)))
            df, flag = signalProcessVis(i)
            t1 = df.index[0]
            t2 = df.index[-1]
            d1, d2 = self.t1t2_to_strings(t1, t2)
            exportAPT('{}_{}_{}sps_process.acc'.format(d1, d2, self.e_var.get()), flag)
            self.writing_text.insert(tk.INSERT, output_path + '/' + '{}_{}_{}sps_process.acc'.format(d1, d2,self.e_var.get()) + '\n')
            self.writing_text.update()
            if i == filenames[-1]:
                messagebox.showinfo("Message", "Job complete!")
            
if __name__ == '__main__':
    root = tk.Tk() 
    root.title('CALIBRATE APT - v1.2')     
    root.geometry('800x800')
    window = APT_Calibration(root)
    root.mainloop()