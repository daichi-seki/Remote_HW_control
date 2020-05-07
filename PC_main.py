import time

import PySimpleGUI as sg
import serial
import serial.tools.list_ports

serRead_timeout_sec = 10
Switches = [
    # Name, Default value, key. Sending value will be x * 2^index
    # list can added
    ['Power-On', True, 'PowerOn'],
    ['DebugSW-On', True, 'DebugSW'],
#    ['Ex-SW1-On', False, 'ExSW1'],
#    ['Ex-SW2-On', False, 'ExSW2'],
]

def layout_gen(comlist_ready):

    #Serial port selector
    layout1 = [
        [sg.Listbox(comlist_ready,size=(15,len(comlist_ready)),default_values=comlist_ready[0], key='Com_selected')],
        [sg.Submit(button_text='Open Port')]
    ]

    #HW controler
    layout2 = []
    for i in Switches:
        layout2.append([sg.Checkbox(i[0], default=i[1], key=i[2])])
    layout2.append([sg.Submit(button_text='Send')])

    #clear button
    layout3 = [[sg.Submit(button_text='Clear')]]

    #Message box
    layout4 = [[sg.Multiline(default_text="Please Select Port and Open the Port...", size=(45, 10), key='Messages')]]

    #Merge layout
    layout = [[sg.Frame('Serial Port Selector', layout1), sg.Frame('Hardware control', layout2), sg.Frame("Cmd",layout3)], [sg.Frame('Status window', layout4)]]
    return layout

def send_data_serial(serport,values):
    val = 0
    message_new = []

    for index, sw in enumerate(Switches, start=0):
        val = val + (values[sw[2]] * (2 ** index))

    serport.write(bytes(str(val).encode()))
    message_new.append("REQ : " + str(val))

    serport.flush()
    print(bytes(str(val).encode()))

    i = 0
    while True:
        received_raw = serport.readline()
        if len(received_raw) > 0:
            received_str = received_raw.decode()
            print(received_str)
            print(val)
            if str(val) == received_str:
                message_new.append("ACK : Success (" + str(val) + ")")
                break
            else:
                message_new.append("ACK : Fail wrong data (" + received_str + ")")
                break
        else:
            print("waiting ACK...")

        i = i + 1
        if i > serRead_timeout_sec:
            print("timeout")
            message_new.append("Error : NO ACK Timeout")
            break
    return message_new


def start_control(comlist_ready):
    val = 0

    #Prepare window
    sg.theme('Dark Blue 3')
    window = sg.Window('Switch control for SA Bench ', layout_gen(comlist_ready))

    #Get window event (Comport open)
    while True:
        event, values = window.read()

        if event is None:
            print('exit')
            break

        if event == 'Clear':
            window['Messages'].update("Please Select Port and Open the Port...")
            for i in Switches:
                window[i[2]].update(i[1])

        if event == 'Send':
            sg.popup("Error : Please Open port firstly")

        if event == 'Open Port':
            try:
                with serial.Serial(''.join(values["Com_selected"]), 9600, timeout=1) as serport:
                    window['Messages'].update("READY : Port opened(" + (' '.join(values["Com_selected"])) + ") successfully")

                    #Get window event (Send)
                    while True:
                        event, values = window.read()

                        if event is None:
                            print('exit')
                            break

                        if event == 'Clear':
                            window['Messages'].update("Please Select Port and Open the Port...")
                            for i in Switches:
                                window[i[2]].update(i[1])
                            break

                        if event == 'Send':
                            message_new = send_data_serial(serport, values)
                            window['Messages'].update(str(values["Messages"] + '\n'.join(message_new)))

            except Exception as u :
                sg.popup(u)
                window.close()
                start_control(comlist_ready)
                break
    # while
    window.close()

def search_com_port():
    coms = serial.tools.list_ports.comports()
    comlist = []
    for com in coms:
        comlist.append(com.device)
    print('Connected COM ports: ' + str(comlist))
    return comlist

#--------------- main program ---------------
if __name__ == '__main__':
    
    #check serial port
    comlist_ready = search_com_port()

    if len(comlist_ready) > 0:
        try:
            #start HW settings via Serial
            start_control(comlist_ready)
        except Exception as e:
            sg.popup(e)
            #Retry
            start_control(comlist_ready)
    else:
        sg.popup("No port available from COM1 to COM21.\nPlease Check Serial Connection")
#--------------------------------------------
