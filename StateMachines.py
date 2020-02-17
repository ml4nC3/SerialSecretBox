import random, string


class SecretBoxFSM:
    """Classe générique de la machine à état incluant les attributs et méthodes communes à toutes les difficultés"""
    def __init__(self):
        self._handlers = {}             # Dictionnaire d'association états/comportements
        self._state = None              # Attribut de l'état courant de la machine
        self.passcode_received = False  # Etat de correspondance entre le message reçu et le code interne
        self._passcode = ""             # Code secret de la machine

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
        self._state = handler(serial_com)                 # On exécute la fonction comportement récupérée. Détermine l'état.
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
            serial_com.write(b"Positif")
            return 'OPENED'
        else:
            serial_com.write(self._passcode.encode('ascii'))
            return 'CLOSED'

    def state_opened(self, serial_com):
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

        self._passcode = "".join(random.choices(string.ascii_letters, k=4)) # Regénération du code

        # Appel de la méthode telle qu'écrite dans la classe d'origine, sans le pass check
        # Et non la version surchargée par la classe facile.
        super(SecretBoxEasy, self).run(serial_com)
        return self._state


class SecretBoxHard(SecretBoxFSM):
    """Version héritée de la machine à état avec un comportement de difficulté difficile"""
    def __init__(self):
        super(SecretBoxHard, self).__init__()

    def state_lock1(self):
        pass

    def state_lock2(self):
        pass

    def state_lock3(self):
        pass


class SecretBoxVeryHard(SecretBoxFSM):
    """Version héritée de la machine à état avec un comportement de difficulté très difficile"""
    def __init__(self):
        super(SecretBoxVeryHard, self).__init__()

    def state_lock1(self):
        pass

    def state_lock2(self):
        pass

    def state_lock3(self):
        pass