from .serialhw import SerialDevice

class DLP4Cls(SerialDevice):
    
    def_DLP_IOR4 = [
    #"ON, OFF"
    ['1','Q'],
    ['2','W'],
    ['3','E'],
    ['4', 'R']

    ]

    idx_DLP_IOR4_ON  = 0
    idx_DLP_IOR4_OFF = 1

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
        import time
        print("DLP send serial request")
        print("update request" + str(self.update))
        message_new = []
        sendstrs = str("")
        for index, IsUpdate in enumerate(self.update, start=0):
            if IsUpdate or self.initstate :
                if self.last_req_state[index] == True:
                    send_str = self.def_DLP_IOR4[index][self.idx_DLP_IOR4_ON]
                else:        
                    send_str = self.def_DLP_IOR4[index][self.idx_DLP_IOR4_OFF]
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
        from .cmn_const import def_ser_timeout_sec
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

def send_data_serial_DLP(serport, device, values):
    from .cmn_const import def_switch_list
    newrequest = [False,False,False,False]
    print("send data DLP")
    for index, sw in enumerate(def_switch_list, start=0):
        newrequest[index] = values[sw[2]]
    device.update_requests(newrequest)
    message_new = device.send_serial()

    return message_new