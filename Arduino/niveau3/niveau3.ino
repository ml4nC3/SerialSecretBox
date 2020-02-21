#include <SoftwareSerial.h>

SoftwareSerial moniteur(11, 10);

bool ignore_message(String message) {
  if (message == "SUCCESS"
      or message == "NOT_OPENING"
      or message == "TURNED") {
    return true;
  }
  return false;
}

void setup() {
  moniteur.begin(9600);
  Serial.begin(9600);
  moniteur.println("Demarrage");
  Serial.println("Demarrage");
}

void loop() {
  String message_recu = "";
  String passcode = "";
  char caractere_suivant;
  bool found = false;

  //moniteur.println(Serial.available());
  while (Serial.available() > 0) {
    caractere_suivant = Serial.read();
    message_recu += caractere_suivant;
    delay(3);
  }

  if (message_recu.length() > 0) {
    moniteur.print("Message recu : ");
    moniteur.println(message_recu);

    // Recherche du message dans la liste des messages à ignorer
    found = ignore_message(message_recu);

    if (found == true) {
      if (message_recu == "NOT_OPENING") {
        moniteur.println("Rotation");
        Serial.print("CLK");
        delay(2000);
        Serial.print(passcode);
        moniteur.print("Renvoi du message : ");
        moniteur.println(passcode);
      }
    }

    if (found == false) {
      moniteur.print("Renvoi du message : ");
      moniteur.println(message_recu);
      passcode = message_recu;
      Serial.print(passcode);
    }
  }
  delay(30);
}
