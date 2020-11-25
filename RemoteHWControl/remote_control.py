import PySimpleGUI as sg
import serial

from .layout import layout_gen
from .dlp4 import DLP4Cls
from .uno import UNOCls
from .cmn_const import (def_ser_timeout_sec,
                        def_serial_device_list, def_switch_list)
from .serialhw import search_com_port


def main():

    # check serial port
    comlist_ready = search_com_port()

    if len(comlist_ready) > 0:
        # start HW settings via Serial
        gui_control(comlist_ready)
    else:
        sg.popup(
            "No port available from COM1 to COM21.\nPlease Check Serial Connection")


def gui_control(comlist_ready):

    # Prepare window
    sg.theme('Dark Blue 3')
    window = sg.Window('Switch control for Bench ', layout_gen(comlist_ready))

    # Get window event (Comport open)
    while True:
        event, values = window.read()

        if event is None:
            print('exit')
            break

        if event == 'Clear':
            window['Messages'].update(
                "Please Select Port and Open the Port...")
            for i in def_switch_list:
                window[i[2]].update(i[1])
            window['Com_selected'].update(
                values=search_com_port(), set_to_index=0)

        if event == 'Send':
            sg.popup("Error : Please Open port firstly")

        if event == 'Open Port':
            with serial.Serial(''.join(values["Com_selected"]), 9600, timeout=1) as serport:
                window['Messages'].update(
                    "READY : Port opened(" + (' '.join(values["Com_selected"])) + ") successfully")

                print(values["Device_selected"])

                # Generate Serial device object
                if values["Device_selected"] == ['DLP-IOR4']:
                    Device = DLP4Cls(serport)
                else:
                    Device = UNOCls(serport)

                # Get window event (Send)
                while True:
                    event, values = window.read()

                    if event is None:
                        print('exit')
                        break

                    if event == 'Clear':
                        window['Messages'].update(
                            "Please Select Port and Open the Port...")
                        for i in def_switch_list:
                            window[i[2]].update(i[1])
                        break

                    if event == 'Send':
                        print("Send button")
                        message_new = Device.send_data_serial(values)
                        print(type(message_new))
                        window['Messages'].update(
                            str(values["Messages"] + '\n'.join(message_new)))
                        print(message_new)
    # while
    window.close()


# --------------- main program ---------------
if __name__ == '__main__':

    main()
# --------------------------------------------
