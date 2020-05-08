# Remote_HW_control
Control HW (Relay) by Arduino + PC(python) via Serial communication

# Overall Structure

* Target HW (Power supply(DC12v, AC XXXv), Toggle switch...) 

	--<Power Line ON-OFF for power supply, Signal line>--

* Relay(Xch)

	--<5V Signal Line ON-OFF>--

* Arduino Digital Output 5V

	--<< Arduino software >>--

* Arduino Serial port

	--<Serial connection (USB or RS-232C or..) >--

* PC serial port

	--<< Python software >>--

* GUI

# Requirement

* Python 3.X
* Arduino UNO R3

# Installation

Install Pyserial and PySimpleGUI with pip command.

```bash
pip install pyserial
pip install pysimplegui
```

# Note

I don't test environments under Linux and Mac.

# Author

* Daichi
