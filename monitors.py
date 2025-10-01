#import pygame
#import pygame_gui
from datetime import datetime, timezone
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
import matplotlib as mpl
import matplotlib.font_manager as fm
from pathlib import Path

class Monitor:
    def __init__(self,
                 pin,
                 plotlabels,
                 keepdata_trelative0: int = -60,
                 update_freq=1):
                 #plot_n: int = 1000,
                 #dt_rolling = 50):
                 #ma=3):
        self.pin = pin
        # self.dt_rolling = dt_rolling
        self.plot_size_inches = [4, 2]
        self.update_freq = update_freq
        #self.plot_n = plot_n
        self._set_updated_epoch()

        #plot parameters:
        #self.ma = ma
        #self.store_moving_average_calculation = np.zeros((self.plot_n, self.ma))

        self.recent_t = [self.t_updated_ts] #log here
        self.recent_y = [0] #log here

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
        self.set_trelative(keepdata_trelative0)
        for idx, label in enumerate(plotlabels):
            line = ax.plot([0], [0], color=cols[idx], marker='None')
            self.plot_elements[label] =  [line]

        #line_up = ax.plot(plot_trelative, self.plot_y, color='yellow', marker='None')
        #line_down = ax.plot(plot_trelative, self.plot_y, color='yellow', marker='None')

    def _set_updated_epoch(self):
        t_now = datetime.now(tz=timezone.utc)
        t_now_ts = datetime.timestamp(t_now)
        self.t_updated_ts = t_now_ts

    def set_trelative(self, keepdata_trelative):
        #self.plot_trelative = np.linspace(keepdata_trelative, 0, self.plot_n)
        self.keepdata_trelative = keepdata_trelative

    def _collect_measurement(self):
        #return some dummy data:
        return self.recent_y[-1] + 0.1*(np.random.rand(1)[0]-0.5)

    def collect(self):#, dt_min = 0):
        self._set_updated_epoch()

        #clear old data:
        for idxt_rec in range(len(self.recent_t)):
            if self.recent_t[idxt_rec] - self.t_updated_ts >= self.keepdata_trelative:#self.plot_trelative[0]:
                break
        self.recent_t = self.recent_t[idxt_rec:]
        self.recent_y = self.recent_y[idxt_rec:]


        if self.t_updated_ts - self.recent_t[-1] < self.update_freq:
            return

        # #wait for next measurement
        # if t_now_ts - self.recent_t[-1] < dt_min:
        #     pygame.time.wait(round(1000*(t_now_ts - self.recent_t[-1])))

        #get measurement at t_now:
        y = self._collect_measurement()
        #add new data:
        if not np.isnan(y):
            self.recent_t.append(self.t_updated_ts)
            self.recent_y.append(y)

        # idxt_rec = 0
        # while self.recent_t[idxt_rec] - t_now_ts >= self.keepdata_trelative:#self.plot_trelative[0]:
        #     idxt_rec = idxt_rec + 1

    def log_to_disk(self):
        #store the raw data
        #recalculate NOBS, mean, etc.
        pass

    # def interpolate_data_to_plot_axis(self):
    #     #interpolate new plot arrays, then delete old data:
    #     plot_y = [self.recent_y[-1]] #got the first element at delta t = 0
    #
    #     idx_ti0 = len(self.recent_t) - 1 #save time by initializing here, this will always descend in the below loop
    #     for t_delta in self.plot_trelative[::-1][1:]:
    #         #[::-1] because we go from delta t = 0 to self.keepdata_trelative (i.e. - 60)
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

        # line[0].set_xdata(self.plot_trelative)
        # line[0].set_ydata(ymean)
        #line_up[0].set_ydata(ymin)
        #line_down[0].set_ydata(ymax)
        recent_t_np = np.array(self.recent_t)
        line[0].set_xdata(recent_t_np - self.t_updated_ts)
        line[0].set_ydata(self.recent_y)

        #self.ax.set_xlim([self.plot_trelative[0], 0])
        self.ax.set_xlim([self.keepdata_trelative, 0])
        self.ax.set_ylim([min(self.recent_y), max(self.recent_y)])
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
                 keepdata_trelative0: int = -30,
                 update_freq=1):
        super().__init__(pin=pin,
                         plotlabels=plotlabels,
                         keepdata_trelative0=keepdata_trelative0,
                         update_freq=update_freq)
        #calibration parameters:
        self.A = 3.3321857915133117
        self.B = 144.7427590102809
        # sensor reading = (A*pressure + B) * gain
        self.ax.set_ylabel('PSI', font=self.fpath, ha='right', va='top', fontsize=15)
        self.ax.yaxis.set_label_coords(0.02, 0.98)
        self.ax.set_xlabel('time [s]', font=self.fpath, ha='right', va='bottom', fontsize=15)
        self.ax.xaxis.set_label_coords(0.98, 0.02)


    def _collect_measurement(self):
        return self.recent_y[-1] + 0.1*(np.random.rand(1)[0]-0.5)
        # sensor reading = (A*pressure + B) * gain