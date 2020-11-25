import time

import PySimpleGUI as sg
import serial
import serial.tools.list_ports


def sendSerial(serport, ports_used):
    i = 0
    while True:
        String_data = serport.readline()
        if len(String_data) > 0:
            print(String_data)

#               if i < 3:
            if True:
                serport.write(String_data)
            # fault injection
            elif i < 5:
                i = i
            # fault injection
            else:
                serport.write("2".encode())
                print("send i")
            i = i + 1

            print(String_data.decode())
            serport.flush()
            print("ACK SENT...")
            # break
        print("waiting for Request...")


def search_com_port():
    coms = serial.tools.list_ports.comports()
    comlist = []
    for com in coms:
        comlist.append(com.device)
    print('Connected COM ports: ' + str(comlist))

    # chose your port
    use_port = comlist[1]
    print('Use COM port: ' + use_port)
    return use_port

# --------------- main program ---------------


if __name__ == '__main__':
    ports_available = search_com_port()
    print(ports_available)

    if len(ports_available) > 0:
        try:
            serport = serial.Serial(ports_available, 9600, timeout=3)
            sendSerial(serport, ports_available)
            serport.close()
        except Exception as e:
            sg.popup(e)
    else:
        sg.popup(
            "No port available from COM1 to COM21.\nPlease Check Serial Connection")
# --------------------------------------------
