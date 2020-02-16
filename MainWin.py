import sys, random, string, serial

# Import des bibliothèques de Qt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer

# Import de la définition de l'interface
from Ui_MainWin import Ui_MainWindow
# Interface créée avec Qt Creator au format .ui et convertie en classe python avec la commande :
# pyuic5 mainwindow.ui -o Ui_MainWin.py

class MainWindow:
    '''Classe de la fenêtre principale de mon ClipFlow Simulator'''
    def __init__(self):
        '''Constructeur de la classe MainWindow'''

        # Initialisation de l'interface graphique
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        # Création du timer
        self._timer = QTimer()

        # Connexion des signaux
        self.ui.btn_start.clicked.connect(self.on_button_click)
        self._timer.timeout.connect(self.on_timer_top)

    def show(self):
        self.main_win.show()

    def on_timer_top(self):
        box_status = box.run(serial_com)
        if box_status == 'CLOSED':
            self.ui.lbl_status.setText("The box is CLOSED.")
        elif box_status == 'OPENED':
            self.ui.lbl_status.setText("The box is OPENED !")

    def on_button_click(self):
        self._timer.start(5000)
        self.ui.lbl_status.setText("Started !")


class SecretBox:
    def __init__(self):
        self._handlers = {'CLOSED': self.state_closed,'OPENED': self.state_opened}
        self.next_state = 'CLOSED'
        self._passcode = "".join(random.choices(string.ascii_letters, k=4))

    def state_closed(self, serial_com):
        incoming_message = serial_com.readline().decode('ascii')
        print(incoming_message)
        if incoming_message == self._passcode:
            serial_com.write(b"Good Game !")
            return 'OPENED'
        else:
            serial_com.write(self._passcode.encode('ascii'))
            return 'CLOSED'

    def state_opened(self, serial_com):
        incoming_message = serial_com.readline().decode('ascii')

        if incoming_message == self._passcode:
            return 'CLOSED'

        serial_com.write(b"I'm opened !")
        return 'OPENED'

    def run(self, serial_com):
        handler = self._handlers[self.next_state]
        self.next_state = handler(serial_com)

        return self.next_state


if __name__ == "__main__":
    print("Starting...")
    app = QApplication(sys.argv)
    # Création de la machine à état
    box = SecretBox()

    # Création de la communication série
    serial_com = serial.Serial('COM2', baudrate=9600, timeout=1)

    # Création de l'application
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
