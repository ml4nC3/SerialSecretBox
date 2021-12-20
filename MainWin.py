# coding=utf-8
import sys
import serial

# Import des bibliothèques de Qt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer

# Import de la définition de l'interface
from Ui_MainWin import Ui_MainWindow
# Interface créée avec Qt Creator au format .ui et convertie en classe python avec la commande :
# pyuic5 mainwindow.ui -o Ui_MainWin.py
import StateMachines as Fsm

# Création de la progression des classes de difficulté
difficulties_handler = [Fsm.SecretBoxEasy,
                        Fsm.SecretBoxMedium,
                        Fsm.SecretBoxHard,
                        Fsm.SecretBoxVeryHard]
# Création des intervalles de timer en fonction de la diffuculté
speed_by_difficulty = [4000, 3000, 2500, 1000]


class MainWindow:
    """Classe de la fenêtre principale de l'application"""

    def __init__(self):
        """Constructeur de la classe MainWindow"""

        # Initialisation de l'interface graphique
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)
        self.ui.lbl_connection_status = "Pas de connexion en cours"

        # Création des objets nécessaires au fonctionnement
        self._timer = QTimer()  # Création du timer de cadencement du jeu
        self.serial_com = None  # Création de l'attribut destiné à l'objet série

        # Connexion des signaux de l'interface avec les méthodes correspondantes
        self.ui.btn_start.clicked.connect(self.on_button_click)
        self._timer.timeout.connect(self.on_timer_top)
        self.ui.lineEdit_port_com.editingFinished.connect(self.on_serial_parameter_change)
        self.ui.spinBox_baudrate.valueChanged.connect(self.on_serial_parameter_change)

        # Initialisation des paramètres
        self._status_message = {'CLOSED': "La boîte est fermée.",
                                'OPENED': "La boite est ouverte !",
                                'LOCK1': "0/3 Verrous ouverts",
                                'LOCK2': "1/3 Verrous ouverts",
                                'LOCK3': "2/3 Verrous ouverts"}
        self._orientation_message = {'UPIGHT': "A plat",
                                     'RIGHT_SIDE': "Sur le côté droit",
                                     'UPSIDE_DOWN': "A l'envers",
                                     'LEFT_SIDE': "Sur le côté gauche"}
        self.serial_settings = {'PORT': 'COM2', 'BAUDRATE': 9600, 'TIMEOUT': 1}  # Paramètres liaison série
        self.current_difficulty = 3
        self.box = None

    def show(self):
        self.main_win.show()

    def on_serial_parameter_change(self):
        self.serial_settings['PORT'] = self.ui.lineEdit_port_com.text()
        self.serial_settings['BAUDRATE'] = self.ui.spinBox_baudrate.value()

    def ui_game_started_mode(self):
        """Mise à jour de l'interface lorsque le jeu démarre"""
        self.ui.spinBox_baudrate.setEnabled(False)
        self.ui.lineEdit_port_com.setEnabled(False)
        self.ui.pgr_level.setValue(self.current_difficulty)
        self.ui.btn_start.setText("Arrêter")
        self.ui.lbl_status.setText("Démarrage...")

    def ui_game_stopped_mode(self):
        """Mise à jour de l'interface lorsque le jeu est arrêté"""
        self.ui.lbl_status.setText("Hors ligne")
        self.ui.lbl_orientation.setText("A plat")
        self.ui.btn_start.setText("Démarrer")
        self.ui.pgr_level.setValue(self.current_difficulty)
        self.ui.spinBox_baudrate.setEnabled(True)
        self.ui.lineEdit_port_com.setEnabled(True)
        # Arrêt du timer et du port série
        self._timer.stop()
        self.serial_com.close()

    def on_timer_top(self):
        """Méthode appelée à chaque top du Timer"""
        box_status = self.box.run(self.serial_com)  # Exécution du comportement courant de la machine à état
        if box_status == 'OPENED':
            del self.box
            self.box = None
            if self.current_difficulty < 5:
                self.current_difficulty += 1
            else:
                pass  # TODO développer la fin de jeu
            # Mise à jour de l'interface en cas de succès
            self.ui_game_stopped_mode()
            message = self._status_message[box_status]  # On récupère le message du statut reçu dans le dictionnaire
            self.ui.lbl_status.setText(message)  # On affiche le message dans l'interface
        else:
            message = self._status_message[box_status]   # On récupère le message du statut reçu dans le dictionnaire
            self.ui.lbl_status.setText(message)         # On affiche le message dans l'interface
            orientation = self.box.get_current_orientation()
            self.ui.lbl_orientation.setText(self._orientation_message[orientation])

    def on_button_click(self):
        # Si la boite est créée, le jeu est donc en cours : arrêt du jeu.
        if self.box is not None:
            self.ui_game_stopped_mode()
            del self.box
            self.box = None
        # Si la boite n'est pas créée, le jeu est arrêté : démarrage.
        elif self.box is None:
            # Création de la communication série
            try:
                self.serial_com = serial.Serial(self.serial_settings['PORT'],
                                                baudrate=self.serial_settings['BAUDRATE'],
                                                timeout=self.serial_settings['TIMEOUT'])
            except:
                self.ui.lbl_status.setText("Erreur port série")
                # TODO afficher l'erreur plutot sur la zone de notification
                return None     # On interrompt la fonction en retournant l'objet None

            # Instanciation de la classe de difficulté correspondante au niveau actuel.
            handler = difficulties_handler[self.current_difficulty]
            self.box = handler()
            self._timer.start(speed_by_difficulty[self.current_difficulty])

            # Mise à jour de l'interface
            self.ui_game_started_mode()
            self.on_timer_top()             # Lancement de la machine à état


if __name__ == "__main__":
    print("Starting Application")
    app = QApplication(sys.argv)

    # Création de l'application
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
