import sys, serial

# Import des bibliothèques de Qt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer

# Import de la définition de l'interface
from Ui_MainWin import Ui_MainWindow
# Interface créée avec Qt Creator au format .ui et convertie en classe python avec la commande :
# pyuic5 mainwindow.ui -o Ui_MainWin.py
import StateMachines as fsm

# Paramètres de la partie
current_difficulty = 0
# Création de la progression des classes de difficulté
difficulties_handler = [fsm.SecretBoxEasy,
                        fsm.SecretBoxMedium,
                        fsm.SecretBoxHard,
                        fsm.SecretBoxVeryHard]
# Création des intervalles de timer en fonction de la diffuculté
speed_by_difficulty = [4000, 3000, 1500, 1000]

class MainWindow:
    """Classe de la fenêtre principale de l'application"""
    def __init__(self):
        """Constructeur de la classe MainWindow"""

        # Initialisation de l'interface graphique
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        # Création du timer permettant l'exécution de la machine à intervalle régulier
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
        self._timer.start(speed_by_difficulty[current_difficulty])
        self.ui.lbl_status.setText("Started !")


if __name__ == "__main__":
    print("Starting Application")
    app = QApplication(sys.argv)

    # Création de la machine à état
    box = fsm.SecretBoxEasy()

    # Création de la communication série
    serial_com = serial.Serial('COM2', baudrate=9600, timeout=1)

    # Création de l'application
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())