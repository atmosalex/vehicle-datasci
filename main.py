import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from math import ceil
import anim_wheel

from datetime import datetime, timezone
import numpy as np

#import pylab
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
clock = pygame.time.Clock()

matplotlib.use("Agg")
plt.rcParams.update({
    "lines.marker": "o",         # available ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', >    "lines.linewidth": "1.8",
    "axes.prop_cycle": plt.cycler('color', ['white']),  # line color
    "text.color": "white",       # no text in this example
    "axes.facecolor": "black",   # background of the figure
    "axes.edgecolor": "lightgray",
    "axes.labelcolor": "white",  # no labels in this example
    "axes.grid": "True",
    "grid.linestyle": "--",      # {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}
    "xtick.color": "white",
    "ytick.color": "white",
    "grid.color": "lightgray",
    "figure.facecolor": "black", # color surrounding the plot
    "figure.edgecolor": "black",
})

class Monitor:
    def __init__(self, pin, dt_rolling = 50, nt = 100):
        t_now = datetime.utcnow()
        t_now_ts = datetime.timestamp(t_now)
        self.pin = pin
        self.dt_rolling = dt_rolling
        self.plot_size_inches = [4, 2]
        self.keepdata_trelative = -30
        self.plot_trelative = np.linspace(self.keepdata_trelative, 0, 200)
        self.plot_y = np.zeros((self.plot_trelative.size))
        self.recent_t = [t_now_ts] #log here
        self.recent_y = [0] #log here
        #self.__create_figure_elements()
    #def __create_figure_elements(self):
        fig = plt.figure(figsize=[self.plot_size_inches[0], self.plot_size_inches[1]], dpi=100)
        fig.patch.set_alpha(0.1) # make the surrounding of the plot 90% transparent
        ax = fig.gca()

        line = ax.plot(self.plot_trelative, self.plot_y, color='red', marker='None')

        #canvas = agg.FigureCanvasAgg(fig)
        self.fig = fig
        self.ax = ax
        self.plot_elements = {label_PRES: line}

    def collect(self):#, dt_min = 0):
        t_now = datetime.utcnow()
        t_now_ts = datetime.timestamp(t_now)

        # #wait for next measurement
        # if t_now_ts - self.recent_t[-1] < dt_min:
        #     pygame.time.wait(round(1000*(t_now_ts - self.recent_t[-1])))

        #get measurement at t_now:
        y = self.recent_y[-1] + 0.1*(np.random.rand(1)[0]-0.5)
        #add new data:
        if not np.isnan(y):
            self.recent_t.append(t_now_ts)
            self.recent_y.append(y)

        #clear old data:
        for idxt_rec in range(len(self.recent_t)):
            if t_now_ts - self.recent_t[idxt_rec] > self.keepdata_trelative:
                break
        self.recent_t = self.recent_t[idxt_rec:]
        self.recent_y = self.recent_y[idxt_rec:]

    def log_to_disk(self):
        #store the raw data
        #recalculate NOBS, mean, etc.
        pass

    def interpolate_data_to_plot_axis(self):
        #interpolate new plot arrays, then delete old data:
        self.plot_y = [self.recent_y[-1]] #got the first element at delta t = 0

        idx_ti0 = len(self.recent_t) - 1 #save time by initializing here, this will always descend in the below loop
        for t_delta in self.plot_trelative[::-1][1:]:
            #[::-1] because we go from delta t = 0 to self.keepdata_trelative (i.e. - 60)
            #[1:] because we already got y at delta t = 0 in the above line
            ti = self.recent_t[-1] + t_delta

            while self.recent_t[idx_ti0] > ti:
                idx_ti0 -= 1
                if idx_ti0 < 0:
                    break
            idx_ti1 = idx_ti0 + 1

            if idx_ti1 == 0:
                #fill the rest with nans and break
                self.plot_y = self.plot_y + [np.nan] * (len(self.plot_trelative) - len(self.plot_y))
                break
            else:
                frac = (ti - self.recent_t[idx_ti0]) / (self.recent_t[idx_ti1] - self.recent_t[idx_ti0])

            self.plot_y.append(self.recent_y[idx_ti0] + frac * (self.recent_y[idx_ti1] - self.recent_y[idx_ti0]))

            #if len(self.recent_t) == 10:
            #    print(self.recent_t[idx_ti0] - t_now_ts, ti - t_now_ts, self.recent_t[idx_ti1] - t_now_ts)
            #    print("", idx_ti0, idx_ti1, len(self.recent_t), frac)#,  ti - t_now_ts, [t_ - t_now_ts for t_ in self.recent_t])

        self.plot_y = np.array(self.plot_y[::-1])

    def get_updated_figure(self, pe_key, ma=15):
        self.interpolate_data_to_plot_axis()

        #perform a moving average, but keep the array size the same, so the beginning and end values are not affected:
        av = np.zeros(self.plot_y.size)
        for r in range((ma // 2), 0, -1): #i.e. 3, 2, 1
            av[r:] = av[r:] + np.roll(self.plot_y, r)[r:]
            av[:r] = av[:r] + self.plot_y[:r] #copy the values
        av = av + self.plot_y #index offset 0
        for r in range(-1, -1 * ceil(ma / 2), -1): #i.e. -1, -2
            av[:r] = av[:r] + np.roll(self.plot_y, r)[:r]
            av[r:] = av[r:] + self.plot_y[r:] #copy the values
        av = av/ma

        line = self.plot_elements[pe_key]
        line[0].set_ydata(av)

        self.ax.set_ylim([min(self.recent_y), max(self.recent_y)])
        renderer = self.fig.canvas.get_renderer()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        raw_data = renderer.buffer_rgba()
        size = self.fig.canvas.get_width_height()
        plot_image = pygame.image.frombuffer(raw_data, size, "RGBA")
        return plot_image, size



label_PRES = "TRANS"
label_FUEL = "FUEL"
pe_PRES = 0

#set up pressure transducer on pin 0:
pressure = Monitor(0)


#set up main display:
pygame.init()
#pygame.display.set_caption('Interface')
screen_width = 800
screen_height = 400
disp1 = pygame.display.set_mode((screen_width,screen_height))

#create a splash screen animation:
#anim_wheel.splash(disp1, clock, screen_width, screen_height)
disp1.fill((0, 0, 0))

#set up pygame_gui:
manager = pygame_gui.UIManager((800, 600))#, 'data/themes/status_bar_theme.json')
overview = pygame_gui.elements.UITabContainer(pygame.Rect((0, 0), (screen_width, screen_height)), manager, None, object_id=ObjectID('#overview', '@UITabContainer'))
ID_tab1 = overview.add_tab(label_PRES, '#tab_pres')
ID_tab2 = overview.add_tab(label_FUEL, '#tab_fuel')
#print(overview.get_object_ids())
# add a button to tab 2:
pygame_gui.elements.UIButton(pygame.Rect((0, 0), (120, 40)),'button!', manager, container=overview.tabs[ID_tab2]['container'], object_id='#tab_2_button')


#initialize plot:
#pressure.collect()
image_plot0, size = pressure.get_updated_figure(label_PRES)
pgui_plot = pygame_gui.elements.ui_image.UIImage(pygame.Rect((100, 100), (size[0], size[1])),
                                                 image_plot0,
                                                 manager,
                                                 container=overview.tabs[ID_tab1]['container'])


is_running = True
while is_running:
    time_delta = clock.tick(60)/100.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        manager.process_events(event)
    manager.update(time_delta)

    pressure.collect()#dt_min = 1)

    #update plot:
    if overview.get_tab()['text'] == label_PRES:
        image_plot, size = pressure.get_updated_figure(label_PRES)
        # update pygame_gui object showing the plot:
        pgui_plot.set_image(image_plot)

    manager.draw_ui(disp1)

    pygame.display.flip()
    pygame.time.Clock().tick(2000)  # Avoid 100% CPU usage
