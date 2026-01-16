from datetime import datetime, timezone
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
import matplotlib as mpl
import matplotlib.font_manager as fm
from pathlib import Path
import os
import pygame
import pygame_gui
cols = plt.rcParams['axes.prop_cycle'].by_key()['color']
dir_log = "log"
fname_pressure_calibration_default = "pressure_calibration_default.txt"
fname_pressure_calibration_current = "pressure_calibration_current.txt"

def load_fuel_settings():
    sep = ','
    def load_dict_from_file(fname, sep=','):
        dic = {}
        with open(fname, 'r') as fi:
            content = fi.readlines()
        for line in content:
            sline = line.strip('\n').split(sep)
            dic[sline[0]] = float(sline[1])
        return dic

    default = load_dict_from_file(fname_pressure_calibration_default, sep)

    if not os.path.isfile(fname_pressure_calibration_current):
        with open(fname_pressure_calibration_current, 'w') as fo:
            for key in default.keys():
                fo.write("{}{}{}\n".format(key, sep, default[key]))
        current = dict(default)
    else:
        current = load_dict_from_file(fname_pressure_calibration_current)

    return default, current

class Monitor:
    def __init__(self,
                 pin,
                 plotlabels,
                 manager,
                 plotcontainer,
                 t0_plot_relative: int = -60,
                 update_ival=1,
                 log_len = 300,):
        self.pin = pin
        self.plot_size_inches = [4, 2]
        self.update_ival = update_ival
        self._set_updated_epoch()
        if log_len/update_ival % 1 != 0:
            print("error: update interval [s] must be a factor of log length [s]")
        self.session_count = 0

        if not os.path.exists(dir_log):
            print("making directory {}".format(dir_log))
            os.mkdir(dir_log)

        fig = plt.figure(figsize=[self.plot_size_inches[0], self.plot_size_inches[1]], dpi=100)
        fig.patch.set_alpha(0.1) # make the surrounding of the plot 90% transparent
        ax = fig.gca()
        self.fpath = Path("Roboto_Mono_static/RobotoMono-Regular.ttf")
        fe = fm.FontEntry(fname=self.fpath, name='RobotoMono-Regular')
        fm.fontManager.ttflist.insert(0, fe)
        mpl.rcParams['font.family'] = fe.name

        self.custom_font = fm.FontProperties(fname=self.fpath)
        self.fig = fig
        self.ax = ax
        self.ax.tick_params(axis='x', labelsize=12)#, fontproperties=self.custom_font)
        self.ax.tick_params(axis='y', labelsize=10)#, fontproperties=self.custom_font)
        #self.ax.set_xticklabels(labels=self.ax.get_xticklabels(), fontproperties=self.custom_font)
        for text_obj in ax.get_xticklabels():
            text_obj.set_fontname('RobotoMono-Regular')
        for text_obj in ax.get_yticklabels():
            text_obj.set_fontname('RobotoMono-Regular')
        #cols = ['red'] #update this with a range of colors to choose from

        #initialize line for each parameter:
        self.plot_elements_lines = {}
        self.plot_elements_idx = {}
        self.set_t0_plot_relative(t0_plot_relative)
        self.y0_fixed = None
        self.y1_fixed = None

        for idx, label in enumerate(plotlabels):
            self.plot_elements_idx[label] = idx
            line = ax.plot([0], [0], color=cols[idx], marker='None')
            self.plot_elements_lines[label] =  [line]

        #initialize arrays to log data:
        self.log_time = np.zeros((1, 1 + int(log_len/update_ival)))
        self.log_elements = np.zeros((len(self.plot_elements_idx), 1 + int(log_len/update_ival)))
        self.log_file_prefix = None
        self.log_enabled = True

        #update figure buffer:
        self.update_figbuffer()

        #initial image to display:
        image_plot0 = pygame.image.frombuffer(self.figbuffer_raw_data, self.figbuffer_size, "RGBA")
        self.pgui_plot = pygame_gui.elements.ui_image.UIImage(pygame.Rect((0, 0), (self.figbuffer_size[0], self.figbuffer_size[1])),
                                                              image_plot0,
                                                              manager,
                                                              container=plotcontainer)

    def _collect_measurement(self, element_idx):
        return self.log_elements[element_idx][-1] + 0.1*(np.random.rand(1)[0]-0.5)

    def _set_updated_epoch(self):
        t_now = datetime.now(tz=timezone.utc)
        t_now_ts = datetime.timestamp(t_now)
        self.t_updated_ts = t_now_ts

    def set_t0_plot_relative(self, tplotrange):
        self.tplotrange = tplotrange

    def set_y0_plot(self, y0):
        self.y0_fixed = y0

    def set_y1_plot(self, y1):
        self.y1_fixed = y1

    def collect(self, element_idx=0):#, dt_min = 0):
        self._set_updated_epoch()
        if self.t_updated_ts - self.log_time[0][-1] < self.update_ival:
            return

        #roll data back:
        self.log_time[:,:-1] = self.log_time[:,1:]
        self.log_elements[:,:-1] = self.log_elements[:,1:]

        #get new measurement at t_now:
        y = self._collect_measurement(element_idx)

        #add new data:
        self.log_time[0,-1] = self.t_updated_ts
        # time is stored at element 0, so increment by 1:
        self.log_elements[element_idx,-1] = y

        self.session_count = self.session_count + 1
        if self.session_count % (self.log_elements.shape[1] - 1) == 0:
            self.log_to_disk()


    def log_to_disk(self, prefix="sensor"):
        #store the raw data
        #self.log_elements
        #print("logging at t={}".format(self.t_updated_ts))
        #raise NotImplementedError
        if self.log_enabled and self.log_file_prefix is not None:
            print("LOG")
        #np.save(os.path.join(dir_log, '{:.0f}_{}.npy'.format(self.log_time[0, -1], prefix)), self.log_elements[:, 1:]) #<-- log these indicies


    def update_figbuffer(self):
        #plot_y = self.interpolate_data_to_plot_axis()

        # #perform a moving average, but keep the array size the same, so the beginning and end values are not affected:
        # row = 0
        # av = self.store_moving_average_calculation
        # for r in range((self.ma // 2), 0, -1): #i.e. 3, 2, 1
        #     av[r:,row] = np.roll(plot_y, r)[r:]
        #     av[:r,row] = plot_y[:r] #copy the values
        #     row = row + 1
        # av[:,row] = plot_y[:] #index offset 0
        # row = row + 1
        # for r in range(-1, -1 * ceil(self.ma / 2), -1): #i.e. -1, -2
        #     av[:r,row] = np.roll(plot_y, r)[:r]
        #     av[r:,row] = plot_y[r:] #copy the values
        #     row = row + 1
        # ymean = np.mean(av,axis=1)
        for label, line_collection in self.plot_elements_lines.items():
            line = line_collection[0][0]
            idx = self.plot_elements_idx[label]

            line.set_xdata(self.log_time[0, :] - self.t_updated_ts)
            line.set_ydata(self.log_elements[idx, :])

            #update plot axis display range, etc.:
            self.ax.set_xlim([self.tplotrange, 0])
            if self.y0_fixed is not None:
                y0 = self.y0_fixed
            else:
                y0 = np.nanmin(self.log_elements[idx, :])
            if self.y1_fixed is not None:
                y1 = self.y1_fixed
            else:
                y1 = np.nanmax(self.log_elements[idx, :])
            self.ax.set_ylim([y0, y1])

        renderer = self.fig.canvas.get_renderer()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        self.figbuffer_raw_data = renderer.buffer_rgba()
        self.figbuffer_size = self.fig.canvas.get_width_height()

class Fuel(Monitor):
    def __init__(self,
                 pin,
                 plotlabels,
                 manager,
                 plotcontainer,
                 t0_plot_relative: int = -300,
                 update_ival=1,
                 log_len = 300,
                 y0_fixed = 0,
                 y1_fixed = 14):
        super().__init__(pin=pin,
                         plotlabels=plotlabels,
                         manager = manager,
                         plotcontainer=plotcontainer,
                         t0_plot_relative=t0_plot_relative,
                         update_ival=update_ival,
                         log_len=log_len)
        self.log_file_prefix = "log_fuel"
        self.y0_fixed = y0_fixed
        self.y1_fixed = y1_fixed
        self.ax.set_ylabel('Volts', font=self.fpath, ha='right', va='top', fontsize=15)
        self.ax.yaxis.set_label_coords(0.02, 0.98)
        self.ax.set_xlabel('time [s]', font=self.fpath, ha='right', va='bottom', fontsize=15)
        self.ax.xaxis.set_label_coords(0.98, 0.02)


    def _collect_measurement(self, element_idx):
        # the following parameters are used in the circuit:
        gain = 8
        R1 = 100000 #voltage divider R1
        R2 = 10000 #voltage divider R2
        ratio_Vadc_Vsensor = 1 - R1 / (R1 + R2)  # <= 1 # the ratio of ADC input voltage to sensor voltage

        # sensor_voltage = (A*pressure + B)
        # ADC_input_voltage = (A*pressure + B) * ratio_Vadc_Vsensor
        # reading = (A*pressure + B) * gain * ratio_Vadc_Vsensor
        #   this is the data I collected for various known pressure
        #   I rearranged for:
        # reading / gain / ratio_Vadc_Vsensor = A * pressure + B
        #   then fit the data to get:
        self.A, self.B = [36.654043693598396, 1592.1703502859946]

        # take a new reading:
        reading = ((self.log_elements[element_idx, -1] * self.A) + self.B) * gain * ratio_Vadc_Vsensor + 2000 * (np.random.rand(1)[0] - 0.5)
        fuel = (reading / gain / ratio_Vadc_Vsensor - self.B)/self.A
        return np.abs(fuel)*0.1

class Battery(Monitor):
    def __init__(self,
                 pin,
                 plotlabels,
                 manager,
                 plotcontainer,
                 t0_plot_relative: int = -300,
                 update_ival=1,
                 log_len = 300,
                 y0_fixed = 0,
                 y1_fixed = 14):
        super().__init__(pin=pin,
                         plotlabels=plotlabels,
                         manager = manager,
                         plotcontainer=plotcontainer,
                         t0_plot_relative=t0_plot_relative,
                         update_ival=update_ival,
                         log_len=log_len)
        self.log_file_prefix = None #no need to log battery voltage
        self.y0_fixed = y0_fixed
        self.y1_fixed = y1_fixed
        self.ax.set_ylabel('Volts', font=self.fpath, ha='right', va='top', fontsize=15)
        self.ax.yaxis.set_label_coords(0.02, 0.98)
        self.ax.set_xlabel('time [s]', font=self.fpath, ha='right', va='bottom', fontsize=15)
        self.ax.xaxis.set_label_coords(0.98, 0.02)

    def _collect_measurement(self, element_idx):
        return 12

class MSP600(Monitor):
    def __init__(self,
                 pin,
                 plotlabels,
                 manager,
                 plotcontainer,
                 t0_plot_relative: int = -60,
                 update_ival=1,
                 log_len = 300,):
        super().__init__(pin=pin,
                         plotlabels=plotlabels,
                         manager = manager,
                         plotcontainer=plotcontainer,
                         t0_plot_relative=t0_plot_relative,
                         update_ival=update_ival,
                         log_len=log_len)

        self.log_file_prefix = "log_fuel"
        self.ax.set_ylabel('PSI', font=self.fpath, ha='right', va='top', fontsize=15)
        self.ax.yaxis.set_label_coords(0.02, 0.98)
        self.ax.set_xlabel('time [s]', font=self.fpath, ha='right', va='bottom', fontsize=15)
        self.ax.xaxis.set_label_coords(0.98, 0.02)

        self.settings_default, self.settings_current = load_fuel_settings()
        print("loaded pressure transducer circuit parameters:", self.settings_default)

    def restore_default_settings(self):
        self.settings_current = dict(self.settings_default)
        if os.path.exists(fname_pressure_calibration_current):
            os.remove(fname_pressure_calibration_current)

    def _collect_measurement(self, element_idx):
        # the following parameters are used in the circuit:
        gain = self.settings_current['gain']#8
        R1 = self.settings_current['R1']#100000 #voltage divider R1
        R2 = self.settings_current['R2']#10000 #voltage divider R2
        ratio_Vadc_Vsensor = 1 - R1 / (R1 + R2)  # <= 1 # the ratio of ADC input voltage to sensor voltage

        # sensor_voltage = (A*pressure + B)
        # ADC_input_voltage = (A*pressure + B) * ratio_Vadc_Vsensor
        # reading = (A*pressure + B) * gain * ratio_Vadc_Vsensor
        #   this is the data I collected for various known pressure
        #   I rearranged for:
        # reading / gain / ratio_Vadc_Vsensor = A * pressure + B
        #   then fit the data to get:
        self.A, self.B = [self.settings_current['A'], self.settings_current['B']]#[36.654043693598396, 1592.1703502859946]

        # take a new reading:
        reading = ((self.log_elements[element_idx, -1] * self.A) + self.B) * gain * ratio_Vadc_Vsensor + 2000 * (np.random.rand(1)[0] - 0.5)
        pressure = (reading / gain / ratio_Vadc_Vsensor - self.B)/self.A
        return pressure
