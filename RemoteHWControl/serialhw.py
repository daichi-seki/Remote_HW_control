class SerialDevice():
    def __init__(self):
        self.devname = 'Default'

    def dev_name(self):

        return self.devname

def search_com_port():
    import serial.tools.list_ports
    coms = serial.tools.list_ports.comports()
    comlist = []
    for com in coms:
        comlist.append(com.device)
    print('Connected COM ports: ' + str(comlist))
    
    return comlist

def send_data_serial(serport, device, values):
    from .dlp4 import send_data_serial_DLP
    from .uno import send_data_serial_UNO

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