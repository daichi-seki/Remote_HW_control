
import serial.tools.list_ports


def search_com_port():

    coms = serial.tools.list_ports.comports()
    comlist = []
    for com in coms:
        comlist.append(com.device)
    print('Connected COM ports: ' + str(comlist))

    return comlist
