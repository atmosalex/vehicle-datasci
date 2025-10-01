import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from math import ceil
import anim_wheel
import sys
from datetime import datetime, timezone
import numpy as np

#import pylab
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg

from monitors import MSP600

class Buttonplacer:
    def __init__(self, dim_ovr_x, dim_ovr_y, dim_ovr_w, dim_ovr_h):
        self.dim_ovr_x, self.dim_ovr_y, self.dim_ovr_w, self.dim_ovr_h = dim_ovr_x, dim_ovr_y, dim_ovr_w, dim_ovr_h
        self.dim_but_w = 120
        self.dim_but_h = 40
        self.dim_but_pad = 1

    def placetopright(self, i):
        return pygame.Rect((self.dim_ovr_w - self.dim_but_w - self.dim_but_pad, self.dim_but_pad+ (i-1)*(2*self.dim_but_pad + self.dim_but_h)), (self.dim_but_w, self.dim_but_h))

np.random.seed(532)
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

label_PRES = " TRANS "
label_FUEL = " FUEL  "
label_BATT = " BATT  "
pe_PRES = 0

#set up pressure transducer on pin 0:
pressure = MSP600(0, plotlabels = [label_PRES], ma=3)


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
manager = pygame_gui.UIManager((800, 600), 'theme.json')
rect_screen = pygame.Rect((0, 0), (screen_width, screen_height))
overview = pygame_gui.elements.UITabContainer(rect_screen, manager, None,
                                              )#button_height=50)#, class_id='@UITabContainer'))
ID_tab1 = overview.add_tab(label_PRES, '#tab_button')
ID_tab2 = overview.add_tab(label_FUEL, '#tab_button')
ID_tab3 = overview.add_tab(label_BATT, '#tab_button')
overview.set_dimensions((screen_width, screen_height), clamp_to_container=True)
#get the dimensions of space inside each tab:
overview_container = overview.tabs[ID_tab1]['container'].get_container()
dim_ovr_x = overview_container.get_rect().x
dim_ovr_y = overview_container.get_rect().y
dim_ovr_w = overview_container.get_rect().size[0]
dim_ovr_h = overview_container.get_rect().size[1]


#BUTTONS and other interactive elements:
buttonplcr = Buttonplacer(dim_ovr_x, dim_ovr_y, dim_ovr_w, dim_ovr_h)
#trans:
trans_select_60s = pygame_gui.elements.UIButton(buttonplcr.placetopright(1),'-60s', manager,
    container=overview.tabs[ID_tab1]['container'],
    object_id=ObjectID(object_id='#button'))
trans_select_5m = pygame_gui.elements.UIButton(buttonplcr.placetopright(2),'-5m', manager,
    container=overview.tabs[ID_tab1]['container'],
    object_id=ObjectID(object_id='#button'))
#fuel:
pygame_gui.elements.UIButton(buttonplcr.placetopright(1),'12V ulim', manager,
                             container=overview.tabs[ID_tab2]['container'],
                             object_id=ObjectID(object_id='#button'))
pygame_gui.elements.UIButton(buttonplcr.placetopright(2),'10V ulim', manager,
                             container=overview.tabs[ID_tab2]['container'],
                             object_id=ObjectID(object_id='#button'))
pygame_gui.elements.UIButton(buttonplcr.placetopright(3),'-20m', manager,
                             container=overview.tabs[ID_tab2]['container'],
                             object_id=ObjectID(object_id='#button'))
pygame_gui.elements.UIButton(buttonplcr.placetopright(4),'-60m', manager,
                             container=overview.tabs[ID_tab2]['container'],
                             object_id=ObjectID(object_id='#button'))
pygame_gui.elements.UIButton(buttonplcr.placetopright(5),'-180m', manager,
                             container=overview.tabs[ID_tab2]['container'],
                             object_id=ObjectID(object_id='#button'))
#battery:
pygame_gui.elements.UIButton(buttonplcr.placetopright(1),'6V llim', manager,
                             container=overview.tabs[ID_tab3]['container'],
                             object_id=ObjectID(object_id='#button'))
pygame_gui.elements.UIButton(buttonplcr.placetopright(2),'0V llim', manager,
                             container=overview.tabs[ID_tab3]['container'],
                             object_id=ObjectID(object_id='#button'))


#initialize plot:
#pressure.collect()
raw_data, size = pressure.get_updated_figure(label_PRES)
image_plot0 = pygame.image.frombuffer(raw_data, size, "RGBA")
pgui_plot = pygame_gui.elements.ui_image.UIImage(pygame.Rect((0, 0), (size[0], size[1])),
                                                 image_plot0,
                                                 manager,
                                                 container=overview.tabs[ID_tab1]['container'])


is_running = True
while is_running:
    time_delta = clock.tick(60)/100.0
    for event in pygame.event.get():
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == trans_select_60s:
                pressure.set_trelative(-60)
            elif event.ui_element == trans_select_5m:
                pressure.set_trelative(-300)
        if event.type == pygame.QUIT:
            is_running = False
        manager.process_events(event)
    manager.update(time_delta)

    pressure.collect()#dt_min = 1)

    #update plot:
    if overview.get_tab()['text'] == label_PRES:
        raw_data, size = pressure.get_updated_figure(label_PRES)
        image_plot = pygame.image.frombuffer(raw_data, size, "RGBA")
        # update pygame_gui object showing the plot:
        pgui_plot.set_image(image_plot)

    manager.draw_ui(disp1)

    pygame.display.flip()
    pygame.time.Clock().tick(2000)  # Avoid 100% CPU usage
