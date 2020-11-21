import time

import PySimpleGUI as sg
import serial
import serial.tools.list_ports

def_ser_timeout_sec = 10
def_switch_list = [
    # Name, Default value, key. Sending value will be x * 2^index
    # list can added
    ['Relay1_Power-On', True, 'PowerOn'],
    ['Relay2_DebugSW-On', True, 'DebugSW'],
    ['Relay3_Ex-SW1-On', False, 'ExSW1'],
    ['Relay4_Ex-SW2-On', False, 'ExSW2'],
]

def_serial_device_list = [
    'DLP-IOR4',
    'UNO'
]

def_DLP_IOR4 = [
    #"ON, OFF"
    ['1','Q'],
    ['2','W'],
    ['3','E'],
    ['4', 'R']
]

idx_DLP_IOR4_ON  = 0
idx_DLP_IOR4_OFF = 1

def layout_gen(comlist_ready):
    #Device selector
    layout1 = [
        [sg.Listbox(comlist_ready, size=(15, len(comlist_ready)), default_values=comlist_ready[0], key='Com_selected')],
        [sg.Listbox(def_serial_device_list,size=(15,len(def_serial_device_list)),default_values=def_serial_device_list[0], key='Device_selected')],
        [sg.Submit(button_text='Open Port')]
    ]
    #HW controler
    layout2 = []
    for i in def_switch_list:
        layout2.append([sg.Checkbox(i[0], default=i[1], key=i[2])])
    layout2.append([sg.Submit(button_text='Send')])
    #clear button
    layout3 = [[sg.Submit(button_text='Clear')]]
    #Message box
    layout4 = [[sg.Multiline(default_text="Please Select Port and Open the Port...", size=(45, 10), key='Messages')]]
    #Merge layout
    layout = [[sg.Frame('Device Settings', layout1), sg.Frame('Hardware control', layout2), sg.Frame("Cmd",layout3)], [sg.Frame('Status window', layout4)]]
    
    return layout

def send_data_serial(serport, device, values):
    print("def send data serial")

    if device.dev_name() == 'DLP-IOR4':
        print("DLP selected")
        message_t = send_data_serial_DLP(serport, device, values)
    elif device.dev_name() == 'UNO':
        print("UNO selected")
        message_t = send_data_serial_UNO(serport, values)
    else:
        assert False,"NO device"

    return message_t

class SerialDevice():
    def __init__(self):
        self.devname = 'Default'

    def dev_name(self):

        return self.devname

class DLP4Cls(SerialDevice):
    def __init__(self, serport):
        self.devname = 'DLP-IOR4'
        self.current_state = [False,False,False,False]
        self.update = [True, True, True, True]
        self.serport = serport
        self.initstate = True

    def update_requests(self, req_state):
        print("DLP update request")
        print("req_state : " + str(req_state))
        print("current_state : " + str(self.current_state))
        for index, i in enumerate(req_state, start = 0):
            if i == self.current_state[index]:
                self.update[index] = False
            else:
                self.update[index] = True
        self.last_req_state = req_state

        return self.update
    
    def send_serial(self):
        print("DLP send serial request")
        print("update request" + str(self.update))
        message_new = []
        sendstrs = str("")
        for index, IsUpdate in enumerate(self.update, start=0):
            if IsUpdate or self.initstate :
                if self.last_req_state[index] == True:
                    send_str = def_DLP_IOR4[index][idx_DLP_IOR4_ON]
                else:        
                    send_str = def_DLP_IOR4[index][idx_DLP_IOR4_OFF]
                self.serport.write(bytes(send_str.encode()))
                self.serport.flush()
                time.sleep(0.1)

                sendstrs += str(send_str)
            else:
                sendstrs += str("_")

        self.update = [False,False,False,False]
        self.current_state = self.last_req_state
        print("DLP Finish send serial request")
        self.initstate = False
        print(sendstrs)
        message_new.append("REQ : " + str(sendstrs))
        ping_result  = self.ping()
        message_new.extend(ping_result)

        return (message_new)
    
    def ping(self):
        send_str = "'"
        message_new = []

        self.serport.write(bytes(send_str.encode()))
        self.serport.flush()
        i = 0
        while True:
            received_raw = self.serport.readline()
            if len(received_raw) > 0:
                received_str = received_raw.decode()
                print(received_str)
                if str("R") == received_str:
                    message_new.append("PING : Success (" + str("R") + ")")
                    break
                else:
                    message_new.append("PING : Fail wrong data (" + received_str + ")")
                    break
            else:
                i = i + 1
                print("waiting PING response ...")
                if i == (def_ser_timeout_sec // 2):
                    self.serport.write(bytes(str(send_str).encode()))
                    message_new.append("RETRY : PING Resending..")
                if i > def_ser_timeout_sec:
                    print("timeout")
                    message_new.append("Error : NO PING RES Timeout")
                    break
        
        return message_new


class UNOCls(SerialDevice):
    def __init__(self, serport):
        self.serport = serport
        self.devname = 'UNO'

def send_data_serial_DLP(serport, device, values):
    newrequest = [False,False,False,False]
    print("send data DLP")
    for index, sw in enumerate(def_switch_list, start=0):
        newrequest[index] = values[sw[2]]
    device.update_requests(newrequest)
    message_new = device.send_serial()

    return message_new

def send_data_serial_UNO(serport,values):
    val = 0
    message_new = []

    for index, sw in enumerate(def_switch_list, start=0):
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
            i = i + 1
            print("waiting ACK...")
            if i == (def_ser_timeout_sec // 2):
                serport.write(bytes(str(val).encode()))
                message_new.append("RETRY : Resending..")
            if i > def_ser_timeout_sec:
                print("timeout")
                message_new.append("Error : NO ACK Timeout")
                break
    return message_new

def start_control(comlist_ready):

    #Prepare window
    sg.theme('Dark Blue 3')
    window = sg.Window('Switch control for Bench ', layout_gen(comlist_ready))

    #Get window event (Comport open)
    while True:
        event, values = window.read()

        if event is None:
            print('exit')
            break

        if event == 'Clear':
            window['Messages'].update("Please Select Port and Open the Port...")
            for i in def_switch_list:
                window[i[2]].update(i[1])

        if event == 'Send':
            sg.popup("Error : Please Open port firstly")

        if event == 'Open Port':
            try:
                with serial.Serial(''.join(values["Com_selected"]), 9600, timeout=1) as serport:
                    window['Messages'].update("READY : Port opened(" + (' '.join(values["Com_selected"])) + ") successfully")

                    print(values["Device_selected"])
                    
                    #Generate Serial device object
                    if values["Device_selected"] == ['DLP-IOR4']:
                        Device = DLP4Cls(serport)
                    else:
                        Device = UNOCls(serport)

                    #Get window event (Send)
                    while True:
                        event, values = window.read()

                        if event is None:
                            print('exit')
                            break

                        if event == 'Clear':
                            window['Messages'].update("Please Select Port and Open the Port...")
                            for i in def_switch_list:
                                window[i[2]].update(i[1])
                            break

                        if event == 'Send':
                            print("Send button")
                            message_new = send_data_serial(serport, Device, values)
                            print(type(message_new))
                            window['Messages'].update(str(values["Messages"] + '\n'.join(message_new)))
                            print(message_new)
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
