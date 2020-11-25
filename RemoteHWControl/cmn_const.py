def_ser_timeout_sec = 10

def_serial_device_list = [

    'DLP-IOR4',
    'UNO'

]

def_switch_list = [
    # Name, Default value, key. Sending value will be x * 2^index
    # list can added
    ['Relay1_Power-On', True, 'PowerOn'],
    ['Relay2_DebugSW-On', True, 'DebugSW'],
    ['Relay3_Ex-SW1-On', False, 'ExSW1'],
    ['Relay4_Ex-SW2-On', False, 'ExSW2'],

]
