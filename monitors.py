from datetime import datetime, timezone
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
import matplotlib as mpl
import matplotlib.font_manager as fm
from pathlib import Path
import os

dir_log = "log"

class Monitor:
    def __init__(self,
                 pin,
                 plotlabels,
                 t0_plot_relative: int = -60,
                 update_ival=1,
                 log_len = 300):
        self.pin = pin
        self.plot_size_inches = [4, 2]
        self.update_ival = update_ival
        self._set_updated_epoch()
        if log_len/update_ival % 1 != 0:
            print("error: update interval [s] must be a factor of log length [s]")
        self.log_chunk = np.zeros((2, 1 + int(log_len/update_ival)))
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
        self.plot_elements = {}#, line_up, line_down]}
        cols = ['red']

        #initial dummy data:
        self.set_t0_plot_relative(t0_plot_relative)
        for idx, label in enumerate(plotlabels):
            line = ax.plot([0], [0], color=cols[idx], marker='None')
            self.plot_elements[label] =  [line]

    def _collect_measurement(self):
        return self.log_chunk[1][-1] + 0.1*(np.random.rand(1)[0]-0.5)

    def _set_updated_epoch(self):
        t_now = datetime.now(tz=timezone.utc)
        t_now_ts = datetime.timestamp(t_now)
        self.t_updated_ts = t_now_ts

    def set_t0_plot_relative(self, tplotrange):
        self.tplotrange = tplotrange

    def collect(self):#, dt_min = 0):
        self._set_updated_epoch()
        if self.t_updated_ts - self.log_chunk[0][-1] < self.update_ival:
            return

        #get new measurement at t_now:
        y = self._collect_measurement()

        #roll data back:
        self.log_chunk[:,:-1] = self.log_chunk[:,1:]

        #add new data:
        self.log_chunk[0,-1] = self.t_updated_ts
        #if not np.isnan(y):
        self.log_chunk[1,-1] = y

        self.session_count = self.session_count + 1
        if self.session_count % (self.log_chunk.shape[1] - 1) == 0:
            self.log_to_disk()


    def log_to_disk(self, prefix="sensor"):
        #store the raw data
        #self.log_chunk
        #print("logging at t={}".format(self.t_updated_ts))
        np.save(os.path.join(dir_log, '{:.0f}_{}.npy'.format(self.log_chunk[0, -1], prefix)), self.log_chunk[:, 1:]) #<-- log these indicies


    def get_updated_figure(self, pe_key):
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

        pe = self.plot_elements[pe_key]
        line = pe[0]

        line[0].set_xdata(self.log_chunk[0, :] - self.t_updated_ts)
        line[0].set_ydata(self.log_chunk[1, :])

        #self.ax.set_xlim([self.plot_trelative[0], 0])
        self.ax.set_xlim([self.tplotrange, 0])
        self.ax.set_ylim([np.nanmin(self.log_chunk[1, :]), np.nanmax(self.log_chunk[1, :])])
        renderer = self.fig.canvas.get_renderer()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        raw_data = renderer.buffer_rgba()
        size = self.fig.canvas.get_width_height()
        return raw_data, size

class MSP600(Monitor):
    def __init__(self,
                 pin,
                 plotlabels,
                 t0_plot_relative: int = -30,
                 update_ival=1,
                 log_len=300):
        super().__init__(pin=pin,
                         plotlabels=plotlabels,
                         t0_plot_relative=t0_plot_relative,
                         update_ival=update_ival,
                         log_len=log_len)

        self.ax.set_ylabel('PSI', font=self.fpath, ha='right', va='top', fontsize=15)
        self.ax.yaxis.set_label_coords(0.02, 0.98)
        self.ax.set_xlabel('time [s]', font=self.fpath, ha='right', va='bottom', fontsize=15)
        self.ax.xaxis.set_label_coords(0.98, 0.02)

    def _collect_measurement(self):
        # the following parameters are used in the circuit:
        gain = 8
        R1 = 100000 #voltage divider R1
        R2 = 10000 #voltage divider R2
        ratio_Vadc_Vsensor = 1 - R1 / (R1 + R2)  # <= 1 # the ratio of ADC input voltage to sensor voltage


        # sensor_voltage = (A*pressure + B)
        # ADC_input_voltage = (A*pressure + B) * ratio_Vadc_Vsensor
        # reading = (A*pressure + B) * gain * ratio_Vadc_Vsensor
        #  this is the data I collected for various known pressure
        #  I rearranged for:
        # reading / gain / ratio_Vadc_Vsensor = A * pressure + B
        #  then fit the data to get:
        self.A, self.B = [36.654043693598396, 1592.1703502859946]


        # take a new reading:
        reading = ((self.log_chunk[1, -1] * self.A) + self.B) * gain * ratio_Vadc_Vsensor + 2000 * (np.random.rand(1)[0] - 0.5) #PLACEHOLDER
        pressure = (reading / gain / ratio_Vadc_Vsensor - self.B)/self.A


        return pressure

    # def interpolate_data_to_plot_axis(self):
    #     #interpolate new plot arrays, then delete old data:
    #     plot_y = [self.recent_y[-1]] #got the first element at delta t = 0
    #
    #     idx_ti0 = len(self.recent_t) - 1 #save time by initializing here, this will always descend in the below loop
    #     for t_delta in self.plot_trelative[::-1][1:]:
    #         #[::-1] because we go from delta t = 0 to self.tplotrange (i.e. - 60)
    #         #[1:] because we already got y at delta t = 0 in the above line
    #         ti = self.recent_t[-1] + t_delta
    #
    #         while self.recent_t[idx_ti0] > ti:
    #             idx_ti0 -= 1
    #             if idx_ti0 < 0:
    #                 break
    #         idx_ti1 = idx_ti0 + 1
    #
    #         if idx_ti1 == 0:
    #             #fill the rest with nans and break
    #             plot_y = plot_y + [np.nan] * (self.plot_n - len(plot_y))
    #             break
    #         frac = (ti - self.recent_t[idx_ti0]) / (self.recent_t[idx_ti1] - self.recent_t[idx_ti0])
    #         y = self.recent_y[idx_ti0] + frac * (self.recent_y[idx_ti1] - self.recent_y[idx_ti0])
    #
    #         # #nearest:
    #         # if ti - self.recent_t[idx_ti0] < self.recent_t[idx_ti1] - ti:
    #         #     y = self.recent_y[idx_ti0]
    #         # else:
    #         #     y = self.recent_y[idx_ti1]
    #
    #         plot_y.append(y)
    #
    #         #if len(self.recent_t) == 10:
    #         #    print(self.recent_t[idx_ti0] - t_now_ts, ti - t_now_ts, self.recent_t[idx_ti1] - t_now_ts)
    #         #    print("", idx_ti0, idx_ti1, len(self.recent_t), frac)#,  ti - t_now_ts, [t_ - t_now_ts for t_ in self.recent_t])
    #
    #     plot_y = np.array(plot_y[::-1])
    #     return plot_y
