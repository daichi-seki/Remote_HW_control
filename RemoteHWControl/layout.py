import PySimpleGUI as sg
from .cmn_const import (def_ser_timeout_sec,
                        def_serial_device_list, def_switch_list)


def layout_gen(comlist_ready):

    # Device selector
    layout1 = [
        [sg.Listbox(comlist_ready, size=(15, len(comlist_ready)),
                    default_values=comlist_ready[0], key='Com_selected')],
        [sg.Listbox(def_serial_device_list, size=(15, len(def_serial_device_list)),
                    default_values=def_serial_device_list[0], key='Device_selected')],
        [sg.Button('Open Port'), sg.Button('Clear')]
    ]
    # HW controler
    layout2 = []
    for i in def_switch_list:
        if i[3] == '':
            layout2.append([sg.Checkbox(i[0], default=i[1], key=i[2])])
        else:
            layout2.append([sg.Checkbox(i[0], default=i[1], key=i[2]), sg.Button(i[3])])

    layout2.append([sg.Button('Send')])

    # Message box
    layout4 = [[sg.Multiline(
        default_text="Please Select Port and Open the Port...", size=(45, 10), key='Messages')]]
    # Merge layout
    layout = [[sg.Frame('Device Settings', layout1), sg.Frame(
        'Hardware control', layout2)], [sg.Frame('Status window', layout4)]]

    return layout
