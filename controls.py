import pygame
import pygame_gui
from pygame_gui.core import ObjectID

label_PRES =" TRANS "
label_FUEL =" FUEL  "
label_BATT =" BATT  "
label_SYS = " SYSTM "

class ElementPlacer:
    def __init__(self, dim_ovr_x, dim_ovr_y, dim_ovr_w, dim_ovr_h, dim_but_w = 120, dim_but_h = 40, dim_but_pad = 1):
        self.dim_ovr_x, self.dim_ovr_y, self.dim_ovr_w, self.dim_ovr_h = dim_ovr_x, dim_ovr_y, dim_ovr_w, dim_ovr_h
        self.dim_but_w = dim_but_w
        self.dim_but_h = dim_but_h
        self.dim_but_pad = dim_but_pad

    def placetopright(self, i, j_from_right=1):
        return pygame.Rect((self.dim_ovr_w - (self.dim_but_w - self.dim_but_pad)*j_from_right,
                            self.dim_but_pad+ (i-1)*(2*self.dim_but_pad + self.dim_but_h)),
                           (self.dim_but_w, self.dim_but_h))

def setup_tab_IDs(overview):
    tab_ID_dict = {}
    tab_ID_dict[label_PRES] = overview.add_tab(label_PRES, '#tab_button')
    tab_ID_dict[label_FUEL] = overview.add_tab(label_FUEL, '#tab_button')
    tab_ID_dict[label_BATT] = overview.add_tab(label_BATT, '#tab_button')
    tab_ID_dict[label_SYS] = overview.add_tab(label_SYS, '#tab_button')
    return tab_ID_dict

def setup_elements(overview, manager, tab_ID_dict):
    container_overview = overview._root_container.get_container()
    container_tab1 = overview.tabs[tab_ID_dict[label_PRES]]['container'].get_container()

    # BUTTONS and other interactive elements:
    buttonplcr_overview = ElementPlacer(*container_tab1.get_rect(), dim_but_w=50)  # dim_ovr_x, dim_ovr_y, dim_ovr_w, dim_ovr_h)
    buttonplcr_tab = ElementPlacer(*container_tab1.get_rect())  # dim_ovr_x, dim_ovr_y, dim_ovr_w, dim_ovr_h)

    button_dict = {}
    label_dict = {}
    field_dict = {}

    button_dict['close'] = pygame_gui.elements.UIButton(buttonplcr_overview.placetopright(1),'X', manager, container=container_overview, object_id=ObjectID(object_id='#button'))

    #pressure:
    button_dict[label_PRES] = {}
    cont_pres = overview.tabs[tab_ID_dict[label_PRES]]['container']
    button_dict[label_PRES]['-60s'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(1),'-60s', manager, container=cont_pres, object_id=ObjectID(object_id='#button'))
    button_dict[label_PRES]['-5m'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(2),'-5m', manager, container=cont_pres, object_id=ObjectID(object_id='#button'))

    #fuel:
    button_dict[label_FUEL] = {}
    cont_fuel = overview.tabs[tab_ID_dict[label_FUEL]]['container']
    button_dict[label_FUEL]['14V ulim'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(1),'14V ulim', manager, container=cont_fuel, object_id=ObjectID(object_id='#button'))
    button_dict[label_FUEL]['10V ulim'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(2),'10V ulim', manager, container=cont_fuel, object_id=ObjectID(object_id='#button'))
    button_dict[label_FUEL]['-5m'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(3),'-5m', manager, container=cont_fuel, object_id=ObjectID(object_id='#button'))
    button_dict[label_FUEL]['-30m'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(4),'-30m', manager, container=cont_fuel, object_id=ObjectID(object_id='#button'))
    button_dict[label_FUEL]['-60m'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(5),'-60m', manager, container=cont_fuel, object_id=ObjectID(object_id='#button'))

    #battery:
    button_dict[label_BATT] = {}
    cont_batt = overview.tabs[tab_ID_dict[label_BATT]]['container']
    #button_dict[label_BATT]['6V llim'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(1),'6V llim', manager, container=cont_batt, object_id=ObjectID(object_id='#button'))
    #button_dict[label_BATT]['0V llim'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(2),'0V llim', manager, container=cont_batt, object_id=ObjectID(object_id='#button'))

    #system:
    button_dict[label_SYS] = {}
    cont_sys = overview.tabs[tab_ID_dict[label_SYS]]['container']
    button_dict[label_SYS]['log on'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(4),'log on', manager, container=cont_sys, object_id=ObjectID(object_id='#button'))
    button_dict[label_SYS]['log off'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(5),'log off', manager, container=cont_sys, object_id=ObjectID(object_id='#button'))
    button_dict[label_SYS]['del log'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(7),'del log', manager, container=cont_sys, object_id=ObjectID(object_id='#button'))
    #to control pressure transducer calibrations:
    button_dict[label_SYS]['update'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(7,4),'update', manager, container=cont_sys, object_id=ObjectID(object_id='#button'))
    button_dict[label_SYS]['restore'] = pygame_gui.elements.UIButton(buttonplcr_tab.placetopright(8,4),'restore', manager, container=cont_sys, object_id=ObjectID(object_id='#button'))
    #
    field_dict[label_SYS] = {}
    field_dict[label_SYS]['gain'] = pygame_gui.elements.UITextEntryLine(buttonplcr_tab.placetopright(2,4), manager, container=cont_sys, object_id=ObjectID(object_id='#field'))
    field_dict[label_SYS]['R1'] = pygame_gui.elements.UITextEntryLine(buttonplcr_tab.placetopright(3,4), manager,container=cont_sys, object_id=ObjectID(object_id='#field'))
    field_dict[label_SYS]['R2'] = pygame_gui.elements.UITextEntryLine(buttonplcr_tab.placetopright(4,4), manager, container=cont_sys, object_id=ObjectID(object_id='#field'))
    field_dict[label_SYS]['calib. A'] = pygame_gui.elements.UITextEntryLine(buttonplcr_tab.placetopright(5,4), manager, container=cont_sys, object_id=ObjectID(object_id='#field'))
    field_dict[label_SYS]['calib. B'] = pygame_gui.elements.UITextEntryLine(buttonplcr_tab.placetopright(6,4), manager, container=cont_sys, object_id=ObjectID(object_id='#field'))
    #
    label_dict[label_SYS] = {}
    label_dict[label_SYS]['pres. calib'] = pygame_gui.elements.UILabel(buttonplcr_tab.placetopright(1,5), "pres. calib", manager, container=cont_sys, object_id=ObjectID(object_id='#label'))
    label_dict[label_SYS]['gain:'] = pygame_gui.elements.UILabel(buttonplcr_tab.placetopright(2,5), "gain:", manager, container=cont_sys, object_id=ObjectID(object_id='#label'))
    label_dict[label_SYS]['R1:'] = pygame_gui.elements.UILabel(buttonplcr_tab.placetopright(3,5), "R1:", manager, container=cont_sys, object_id=ObjectID(object_id='#label'))
    label_dict[label_SYS]['R2:'] = pygame_gui.elements.UILabel(buttonplcr_tab.placetopright(4,5), "R2:", manager, container=cont_sys, object_id=ObjectID(object_id='#label'))
    label_dict[label_SYS]['calib. A:'] = pygame_gui.elements.UILabel(buttonplcr_tab.placetopright(5,5), "calib. A:", manager, container=cont_sys, object_id=ObjectID(object_id='#label'))
    label_dict[label_SYS]['calib. B:'] = pygame_gui.elements.UILabel(buttonplcr_tab.placetopright(6,5), "calib. B:", manager, container=cont_sys, object_id=ObjectID(object_id='#label'))
    label_dict[label_SYS]['update OK'] = pygame_gui.elements.UILabel(buttonplcr_tab.placetopright(7, 3), "", manager, container=cont_sys, object_id=ObjectID(object_id='#label'))

    return button_dict, label_dict, field_dict
