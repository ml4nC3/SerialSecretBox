# SerialSercretBox
Serial Secret Box is a simple application that sends a passcode on Serial port and expect it to be resend in order to change state (educationnal purpose).

# Configuration
Currently this application is set to communicate on COM2 at 9600 bauds/s.

The application also requires following librairies installed :
- PyQt5
- PySerial

# Testing
In order to test this application you'll need a serial port virtualizer like VSPE and another application that allows you to receive and write messages on serial port.
