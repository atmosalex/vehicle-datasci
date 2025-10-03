import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from math import ceil
import anim_wheel
import sys
from datetime import datetime, timezone
import numpy as np
import controls
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
from monitors import MSP600

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

log_from_startup = True

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
manager = pygame_gui.UIManager((1200, 800), 'theme.json')
rect_screen = pygame.Rect((0, 0), (screen_width, screen_height))
overview = pygame_gui.elements.UITabContainer(rect_screen, manager, None,
                                              button_height=50)#, class_id='@UITabContainer'))

tab_ID_dict = controls.setup_tab_IDs(overview)

overview.set_dimensions((screen_width, screen_height), clamp_to_container=True)

button_dict = controls.setup_buttons(overview, manager, tab_ID_dict)
if log_from_startup:
    button_dict[controls.label_SYS]['log on'].disable()
else:
    button_dict[controls.label_SYS]['log off'].disable()

#initialize plot:

#set up pressure transducer on pin 0:
pressure = MSP600(0, plotlabels = [controls.label_PRES], update_ival=0.5, log_len=60)

raw_data, size = pressure.get_updated_figure(controls.label_PRES)
image_plot0 = pygame.image.frombuffer(raw_data, size, "RGBA")
pgui_plot = pygame_gui.elements.ui_image.UIImage(pygame.Rect((0, 0), (size[0], size[1])),
                                                 image_plot0,
                                                 manager,
                                                 container=overview.tabs[tab_ID_dict[controls.label_PRES]]['container'])


is_running = True
while is_running:
    time_delta = clock.tick(60)/100.0
    for event in pygame.event.get():
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button_dict['close']:
                is_running = False
            elif event.ui_element == button_dict[controls.label_PRES]['-60s']:
                pressure.set_t0_plot_relative(-60)
            elif event.ui_element == button_dict[controls.label_PRES]['-5m']:
                pressure.set_t0_plot_relative(-300)
            elif event.ui_element == button_dict[controls.label_SYS]['log on']:
                button_dict[controls.label_SYS]['log off'].enable()
                button_dict[controls.label_SYS]['log on'].disable()
            elif event.ui_element == button_dict[controls.label_SYS]['log off']:
                button_dict[controls.label_SYS]['log on'].enable()
                button_dict[controls.label_SYS]['log off'].disable()
        if event.type == pygame.QUIT:
            is_running = False
        manager.process_events(event)
    manager.update(time_delta)

    pressure.collect()

    #update plot:
    if overview.get_tab()['text'] == controls.label_PRES:
        raw_data, size = pressure.get_updated_figure(controls.label_PRES)
        image_plot = pygame.image.frombuffer(raw_data, size, "RGBA")
        # update pygame_gui object showing the plot:
        pgui_plot.set_image(image_plot)

    manager.draw_ui(disp1)

    pygame.display.flip()
    pygame.time.Clock().tick(2000)  # Avoid 100% CPU usage
