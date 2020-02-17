# SerialSercretBox
Serial Secret Box is a simple application that sends a passcode on Serial port and expect it to be resend in order to change state (educationnal purpose).

# Configuration
Currently this application is set to communicate on COM2 at 9600 bauds/s.

The application also requires following librairies installed :
- PyQt5
- PySerial

Additionnaly you'll need softwares to communicate through serial port :
- Virtual Serial Port Emulator (VSPE) : http://www.eterlogic.com/Products.VSPE.html
- Some Serial Port sniffer like freeserialanalyzer (not tested myself) with ability to connect to a port and receive/send message on that port.

# Testing
Testing procedure : 
- Open VSPE, create a new pair and defines port numbers (ex COM1 >> COM2)
- Open your sniffer and connect it to COM1
- Start SerialSecretBox, clicks on start and interract through serial port in order to make it change state.
