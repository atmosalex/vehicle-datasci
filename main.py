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
import monitors

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
overview = pygame_gui.elements.UITabContainer(rect_screen, manager, None, )#button_height=50)#, class_id='@UITabContainer'))

tab_ID_dict = controls.setup_tab_IDs(overview)

overview.set_dimensions((screen_width, screen_height), clamp_to_container=True)

button_dict, label_dict, field_dict = controls.setup_elements(overview, manager, tab_ID_dict)
if log_from_startup:
    button_dict[controls.label_SYS]['log on'].disable()
else:
    button_dict[controls.label_SYS]['log off'].disable()

#initialize plot:

#set up pressure transducer on pin 0:
pressure = monitors.MSP600(pin = 0,
    plotlabels = [controls.label_PRES],
    manager=manager,
    plotcontainer=overview.tabs[tab_ID_dict[controls.label_PRES]]['container'],
    update_ival=0.5,
    log_len=60,)
#set up fuel sender on pin 1:
fuel = monitors.Fuel(pin=1,
    plotlabels = [controls.label_FUEL],
    manager=manager,
    plotcontainer=overview.tabs[tab_ID_dict[controls.label_FUEL]]['container'],
    update_ival=0.5,
    log_len=60)
#set up fuel sender on pin 2:
battery = monitors.Battery(pin=2,
    plotlabels = [controls.label_BATT],
    manager=manager,
    plotcontainer=overview.tabs[tab_ID_dict[controls.label_BATT]]['container'],
    update_ival=0.5,
    log_len=60)

def set_pressure_calib_fields_from_dict(settings_current):
    field_dict[controls.label_SYS]['gain'].set_text('{}'.format(settings_current['gain']))
    field_dict[controls.label_SYS]['R1'].set_text('{}'.format(settings_current['R1']))
    field_dict[controls.label_SYS]['R2'].set_text('{}'.format(settings_current['R2']))
    field_dict[controls.label_SYS]['calib. A'].set_text('{}'.format(settings_current['A']))
    field_dict[controls.label_SYS]['calib. B'].set_text('{}'.format(settings_current['B']))
    label_dict[controls.label_SYS]['update OK'].set_text("")

def set_dict_from_pressure_calib_fields(dict):
    try:
        g = float(field_dict[controls.label_SYS]['gain'].get_text())
        r1 = float(field_dict[controls.label_SYS]['R1'].get_text())
        r2 = float(field_dict[controls.label_SYS]['R2'].get_text())
        A = float(field_dict[controls.label_SYS]['calib. A'].get_text())
        B = float(field_dict[controls.label_SYS]['calib. B'].get_text())
    except:
        label_dict[controls.label_SYS]['update OK'].set_text("FAILED")
        return
    dict['gain'] = g
    dict['R1'] = r1
    dict['R2'] = r2
    dict['A'] = A
    dict['B'] = B
    label_dict[controls.label_SYS]['update OK'].set_text("UPDATED")

set_pressure_calib_fields_from_dict(pressure.settings_current)

is_running = True
while is_running:
    time_delta = clock.tick(60)/100.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            break
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element is button_dict['close']:
                is_running = False
                break
            elif event.ui_element.ui_container is overview.tabs[tab_ID_dict[controls.label_PRES]]['container'].get_container():
                if event.ui_element is button_dict[controls.label_PRES]['-60s']:
                    pressure.set_t0_plot_relative(-60)
                elif event.ui_element is button_dict[controls.label_PRES]['-5m']:
                    pressure.set_t0_plot_relative(-300)
            elif event.ui_element.ui_container is overview.tabs[tab_ID_dict[controls.label_FUEL]]['container'].get_container():
                if event.ui_element is button_dict[controls.label_FUEL]['-5m']:
                    fuel.set_t0_plot_relative(-300)
                elif event.ui_element is button_dict[controls.label_FUEL]['-30m']:
                    fuel.set_t0_plot_relative(-1800)
                elif event.ui_element is button_dict[controls.label_FUEL]['-60m']:
                    fuel.set_t0_plot_relative(-3600)
                elif event.ui_element is button_dict[controls.label_FUEL]['14V ulim']:
                    fuel.y1_fixed = 14
                elif event.ui_element is button_dict[controls.label_FUEL]['10V ulim']:
                    fuel.y1_fixed = 10
            elif event.ui_element.ui_container is overview.tabs[tab_ID_dict[controls.label_BATT]]['container'].get_container():
                pass
            elif event.ui_element.ui_container is overview.tabs[tab_ID_dict[controls.label_SYS]]['container'].get_container():
                if event.ui_element is button_dict[controls.label_SYS]['log on']:
                    button_dict[controls.label_SYS]['log off'].enable()
                    button_dict[controls.label_SYS]['log on'].disable()
                    pressure.log_enabled = True
                    fuel.log_enabled = True
                    battery.log_enabled = True
                elif event.ui_element is button_dict[controls.label_SYS]['log off']:
                    button_dict[controls.label_SYS]['log on'].enable()
                    button_dict[controls.label_SYS]['log off'].disable()
                    pressure.log_enabled = False
                    fuel.log_enabled = False
                    battery.log_enabled = False
                elif event.ui_element is button_dict[controls.label_SYS]['update']:
                    # convert the newly specified parameters to floats and enter into the pressure.settings_current dict
                    set_dict_from_pressure_calib_fields(pressure.settings_current)
                elif event.ui_element is button_dict[controls.label_SYS]['restore']:
                    pressure.restore_default_settings()
                    set_pressure_calib_fields_from_dict(pressure.settings_current)

        manager.process_events(event)
    manager.update(time_delta)

    #collect new measurements:
    pressure.collect()
    fuel.collect()
    battery.collect()

    #update plot:
    match overview.get_tab()['text']:
        case controls.label_PRES:
            pressure.update_figbuffer()
            image_plot = pygame.image.frombuffer(pressure.figbuffer_raw_data, pressure.figbuffer_size, "RGBA")
            pressure.pgui_plot.set_image(image_plot)
        case controls.label_FUEL:
            fuel.update_figbuffer()
            image_plot = pygame.image.frombuffer(fuel.figbuffer_raw_data, fuel.figbuffer_size, "RGBA")
            fuel.pgui_plot.set_image(image_plot)

    manager.draw_ui(disp1)

    pygame.display.flip()
    pygame.time.Clock().tick(2000)  # Avoid 100% CPU usage
