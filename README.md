# Remote_HW_control
Control HW (Relay) by Arduino OR dedicated device (DLP-IOR4)  
+ PC(python) via Serial communication on GUI

# Requirement

## Controller (PC)
* Python 3.X

## Target Module  
1 of folloing HWs
* DLP-IOR4
* Arduino UNO R3 (Sketch included) + Relay Module (genelic one named 4 Channel DC 5V Relay)

# Installation
Install Pyserial and PySimpleGUI with pip command.  
```bash
pip install pyserial
pip install pysimplegui
```

* Exe is included for Windows at /dist/main.exe
* For exe generation, please modify main.spec and run pyinstaller main.spec

# Note
I don't test environments under Linux and Mac.

# Author
* Daichi
