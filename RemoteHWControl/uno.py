from .serialhw import SerialDevice

class UNOCls(SerialDevice):
    def __init__(self, serport):
        self.serport = serport
        self.devname = 'UNO'

def send_data_serial_UNO(serport, values):
    from .cmn_const import def_ser_timeout_sec, def_switch_list
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