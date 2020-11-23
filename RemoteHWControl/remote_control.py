def main():
    import PySimpleGUI as sg
    from .serialhw import search_com_port
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


def start_control(comlist_ready):
    import PySimpleGUI as sg
    import serial
    from .serialhw import send_data_serial
    from .cmn_const import def_serial_device_list, def_switch_list
    from .layout import layout_gen
    from .dlp4 import DLP4Cls
    from .uno import UNOCls

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


#--------------- main program ---------------
if __name__ == '__main__':
    
    main()
#--------------------------------------------
