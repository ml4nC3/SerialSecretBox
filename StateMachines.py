import random
import string
import re


class SecretBoxFSM:
    """Classe générique de la machine à état incluant les attributs et méthodes communes à toutes les difficultés"""
    def __init__(self):
        self._handlers = {}             # Dictionnaire d'association états/comportements
        self._state = None              # Attribut de l'état courant de la machine
        self.passcode_received = False  # Etat de correspondance entre le message reçu et le code interne
        self._passcode = ""             # Code secret de la machine

        self._orientation = 0
        self._orientations = ['UPIGHT', 'RIGHT_SIDE', 'UPSIDE_DOWN', 'LEFT_SIDE']

    def get_current_orientation(self):
        return self._orientations[self._orientation]

    def password_check(self, incoming_message):
        # Methode vérifiant la correspondance d'un message reçu sur le port série avec le code interne
        # Cette étape est isolée dans une méthode afin de pouvoir adapter le moment de son exécution selon la diff
        print(incoming_message)
        if incoming_message == self._passcode:
            self.passcode_received = True
        else:
            self.passcode_received = False

    def run(self, serial_com):
        # Fonction d'éxécution du comportant correspondant à l'état en cours de la machine
        handler = self._handlers[self._state]   # On récupère le nom de la fonction comportement dans le dictionnaire
        self._state = handler(serial_com)       # On exécute la fonction comportement récupérée. Détermine l'état.
        return self._state                      # On retourne l'état à l'appelant afin de pouvoir adapter l'UI


class SecretBoxEasy(SecretBoxFSM):
    """Version héritée de la machine à état avec un comportement de difficulté facile"""
    def __init__(self):
        super(SecretBoxEasy, self).__init__()                                       # Instanciation de la classe parente
        self._passcode = "".join(random.choices(string.ascii_letters, k=4))         # Génération du code
        # Paramétrage des états et comportements de la machine
        self._handlers = {'CLOSED': self.state_closed, 'OPENED': self.state_opened}
        self._state = 'CLOSED'

    def state_closed(self, serial_com):
        # Comportement de la machine à l'état CLOSED
        if self.passcode_received:
            serial_com.write(b"SUCCESS")
            return 'OPENED'
        else:
            serial_com.write(self._passcode.encode('ascii'))
            return 'CLOSED'

    def state_opened(self, serial_com):  # TODO à supprimer/revoir
        # Comportement de la machine à l'état OPENED
        if not self.passcode_received:
            return 'CLOSED'
        serial_com.write(b"I'm opened !")
        return 'OPENED'

    def run(self, serial_com):
        # Surcharge de la méthode d'exécution afin de rajouter la vérification du Code secret
        incoming_message = serial_com.readline().decode('ascii')
        if len(incoming_message) > 0:
            self.password_check(incoming_message)

        # Appel de la méthode telle qu'écrite dans la classe parente
        super(SecretBoxEasy, self).run(serial_com)
        return self._state


class SecretBoxMedium(SecretBoxEasy):
    """Version héritée de la machine à état avec un comportement de difficulté moyenne"""
    def __init__(self):
        super(SecretBoxMedium, self).__init__()

    def run(self, serial_com):
        # On surcharge la méthode run afin de pouvoir vérifier la correspondance du code avant de le regénérer.
        incoming_message = serial_com.readline().decode('ascii')
        if len(incoming_message) > 0:
            self.password_check(incoming_message)

        self._passcode = "".join(random.choices(string.ascii_letters, k=4))  # Regénération du code

        # Appel de la méthode telle qu'écrite dans la classe d'origine, sans le pass check
        # Et non la version surchargée par la classe facile.
        super(SecretBoxEasy, self).run(serial_com)
        return self._state


class SecretBoxHard(SecretBoxFSM):
    """Version héritée de la machine à état avec un comportement de difficulté difficile"""
    def __init__(self):
        super(SecretBoxHard, self).__init__()
        passcode1 = "".join(random.choices(string.ascii_letters, k=4))         # Génération du code
        passcode2 = "".join(random.choices(string.ascii_letters, k=4))
        passcode3 = "".join(random.choices(string.ascii_letters, k=4))
        self._passcode = {'LOCK1': passcode1,
                          'LOCK2': passcode2,
                          'LOCK3': passcode3}
        # Paramétrage des états et comportements de la machine
        self._handlers = {'LOCK1': self.state_lock1,
                          'LOCK2': self.state_lock2,
                          'LOCK3': self.state_lock3}
        self._state = 'LOCK1'
        self.first_run_state = True

    def password_check(self, incoming_message):
        # Surcharge de la fonction de vérification du mot de passe
        print(incoming_message)
        if incoming_message == self._passcode[self._state]:
            self.passcode_received = True
        else:
            self.passcode_received = False

    def state_lock1(self, serial_com):
        # Comportement de la machine à l'état LOCK1
        if self.passcode_received:
            self.passcode_received = False
            return 'LOCK2'
        else:
            serial_com.write(self._passcode[self._state].encode('ascii'))
            return 'LOCK1'

    def state_lock2(self, serial_com):
        # Comportement de la machine à l'état LOCK2
        if self.first_run_state:
            serial_com.write(self._passcode[self._state].encode('ascii'))
            self.first_run_state = False
            return 'LOCK2'
        elif self.passcode_received:
            self.passcode_received = False
            self.first_run_state = True
            return 'LOCK3'
        else:
            serial_com.write(self._passcode[self._state].encode('ascii'))
            return 'LOCK1'

    def state_lock3(self, serial_com):
        # Comportement de la machine à l'état LOCK3
        if self.first_run_state:
            serial_com.write(self._passcode[self._state].encode('ascii'))
            self.first_run_state = False
            return 'LOCK3'
        elif self.passcode_received:
            serial_com.write(b"SUCCESS")
            return 'OPENED'
        else:
            serial_com.write(self._passcode[self._state].encode('ascii'))
            return 'LOCK2'

    def run(self, serial_com):
        # Surcharge de la méthode d'exécution afin de rajouter la vérification du Code secret
        incoming_message = serial_com.readline().decode('ascii')
        if len(incoming_message) > 0:
            self.password_check(incoming_message)

        # Appel de la méthode telle qu'écrite dans la classe parente
        super(SecretBoxHard, self).run(serial_com)
        return self._state


class SecretBoxVeryHard(SecretBoxFSM):
    """Version héritée de la machine générique avec ajout de commandes d'interractions"""
    def __init__(self):
        super(SecretBoxVeryHard, self).__init__()
        # Paramétrage des commandes
        self._expected_format = 'RQ:(.*):(.*)'
        self._handlers = {'TURN': self.on_request_turn,
                          'CODE': self.on_request_code,
                          'POS': self.on_request_orientation,
                          'XPOS': self.on_request_expected_orientation,
                          'UNLK': self.on_request_unlock}
        # Génération des positions attendues pour chaque verrou
        passcode1 = "".join(random.choices(string.ascii_letters, k=4))         # Génération du code
        passcode2 = "".join(random.choices(string.ascii_letters, k=4))
        passcode3 = "".join(random.choices(string.ascii_letters, k=4))
        self._passcode = {passcode1: None,
                          passcode2: None,
                          passcode3: None}
        positions = [0, 1, 2, 3]
        for code in self._passcode.keys():
            choice = random.choice(positions)
            self._passcode[code] = choice
            positions.remove(choice)
        self._state = 'LOCK1'

    def password_check(self, incoming_message):
        pass

    def on_request_orientation(self, serial_com, argument):
        response = str(self._orientation)
        serial_com.write(response.encode('ascii'))
        return 'LOCK1'

    def on_request_expected_orientation(self, serial_com, argument):
        try:
            response = str(self._passcode[argument])
            serial_com.write(response.encode('ascii'))
        except KeyError:
            # Si le code fourni n'est pas dans le dictionnaire
            serial_com.write(b'ERR47')
        return 'LOCK1'

    def on_request_code(self, serial_com, argument):
        codes = list(self._passcode.keys())  # Récupéreration de la liste des codes
        # On essai de récupérer le code correspondant à l'argument passé
        try:
            code_id = int(argument)
            response = str(codes[code_id])
            serial_com.write(response.encode('ascii'))
        except IndexError or ValueError:  # argument hors plage OU argument non entier
            serial_com.write(b'ERR47')
        return 'LOCK1'  # Réintialisation de l'état

    def on_request_turn(self, serial_com, argument):
        try:
            self._orientation = int(argument)
            serial_com.write(b'TURNED')
        except IndexError or ValueError:  # argument hors plage OU argument non entier
            serial_com.write(b'ERR47')
        return self._state  # Conservation de l'état courant

    def on_request_unlock(self, serial_com, argument):
        states = ['LOCK1', 'LOCK2', 'LOCK3', 'OPENED']                # Création de la liste des états
        codes = list(self._passcode.keys())                 # Récupéreration de la liste des codes
        expected_code = codes[states.index(self._state)]    # Détermination du code attendu
        try:
            # Validation du couple code/orientation courante
            assert(self._passcode[argument] == self._orientation)
        except KeyError:
            # Si le code en argument est inconnu
            serial_com.write(b'ERR28')
        except AssertionError:
            # Si la position actuelle ne correspond pas à l'attendue pour le code donné
            serial_com.write(b'ERR12')
        else:
            if argument == expected_code:
                serial_com.write(b'UNLOCKED')
                return states[states.index(self._state) + 1]  # On retourne l'état suivant de celui en cours
        # On réinitialise l'état en cas d'échec
        return 'LOCK1'

    def run(self, serial_com):
        # Surcharge de la méthode d'exécution afin de rajouter la vérification du Code secret
        incoming_message = serial_com.readline().decode('ascii')
        # Vérification du format et extraction de la commande et de l'argument
        if len(incoming_message) > 0:
            # Application de l'expression régulière définie à l'initialisation
            argument = re.match(self._expected_format, incoming_message)
            if argument is None:
                # Si le message reçu ne respecte pas le format
                serial_com.write(b'ERR52')
            elif argument[1] not in list(self._handlers.keys()):
                # Si la commande extraite n'est pas dans la liste des commandes connues
                serial_com.write(b'ERR75')
            else:
                # Explicitation des valeurs récupérées dans le message
                command = argument[1]
                parameter = argument[2]
                # Appel de la méthode correspondante à la commande avec passage de l'argument
                handler = self._handlers[command]
                self._state = handler(serial_com, parameter)
        # TODO développer la réinitialisation du statut si les 3 codes ne sont pas enchaînés
        return self._state
