
from .cmn_const import (def_ser_timeout_sec,
                        def_serial_device_list, def_switch_list)
from .SerialDevice import SerialDeviceCls


class UNOCls(SerialDeviceCls):
    def __init__(self, serport):
        self.serport = serport
        self.devname = 'UNO'

    def send_data_serial(self, values):

        val = 0
        message_new = []

        for index, sw in enumerate(def_switch_list, start=0):
            val = val + (values[sw[2]] * (2 ** index))

        self.serport.write(bytes(str(val).encode()))
        message_new.append("REQ : " + str(val))

        self.serport.flush()
        print(bytes(str(val).encode()))

        i = 0
        while True:
            received_raw = self.serport.readline()
            if len(received_raw) > 0:
                try:
                    received_str = received_raw.decode()
                    print(received_str)
                    print(val)
                    if str(val) == received_str:
                        message_new.append("ACK : Success (" + str(val) + ")")
                        break
                    else:
                        message_new.append(
                            "ACK : Fail wrong data (" + received_str + ")")
                        break
                except Exception as u:
                    print(u)
                    message_new = [
                        "ERROR : Received data is not decodable. Please check COM port"]
                    break
            else:
                i = i + 1
                print("waiting ACK...")
                if i == (def_ser_timeout_sec // 2):
                    self.serport.write(bytes(str(val).encode()))
                    message_new.append("RETRY : Resending..")
                if i > def_ser_timeout_sec:
                    print("timeout")
                    message_new.append("Error : NO ACK Timeout")
                    break
        return message_new
