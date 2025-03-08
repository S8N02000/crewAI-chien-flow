#!/usr/bin/env python
from random import choice
from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start, router, or_

from chien_carac.crews.chien_crew.chien_crew import ChienCrew
from chien_carac.crews.verifier_crew.verifier_crew import VerifierCrew
from chien_carac.crews.fix_crew.fix_crew import FixCrew
from chien_carac.crews.check_race_crew.check_race_crew import CheckRaceCrew
from typing import List


class ChienState(BaseModel):
    """
    Représente l'état du flow contenant les informations d'une fiche de chien.

    Attributs :
    - race (str) : Nom de la race de chien actuellement traitée.
    - fiche (str) : Contenu de la fiche descriptive générée.
    - list_error (List[str]) : Liste des erreurs détectées lors de la vérification.
    """
    race: str = ""
    fiche: str = ""
    list_error: List[str] = Field(default_factory=list)


class ChienFlow(Flow[ChienState]):
    """
    Flow orchestrant la génération, la correction et la vérification 
    des fiches techniques sur les races de chiens.

    Déroulement du flow :
    1️⃣ Sélection d'une race de chien (→ `@start()`)
    2️⃣ Génération de la fiche descriptive (→ `@listen()`)
    3️⃣ Vérification de la fiche générée (→ `@router()`)
    4️⃣ Correction en cas d'erreurs détectées (→ `@listen()`)
    5️⃣ Validation et sauvegarde de la fiche corrigée (→ `@listen()`)
    """

    @start()
    def start(self):
        """
        📌 Étape 1 : Demande à l'utilisateur de saisir une race de chien et vérifie son existence.

        🔹 L'utilisateur entre une race de chien.
        🔹 L'agent 'verificateur_race' valide si elle existe.
        🔹 Si la race est invalide, on redemande une nouvelle entrée.
        """
        race_validee = False
        while not race_validee:
            race_input = input("Veuillez entrer une race de chien : ").strip()
            
            result = CheckRaceCrew().crew().kickoff(inputs={"race": race_input})

            if result.pydantic.Race:
                self.state.race = race_input
                print(f"✅ '{self.state.race}' est une race reconnue.")
                race_validee = True
            else:
                print(f"❌ '{race_input}' n'est pas une race reconnue. {result.pydantic.Message}")
                print("Veuillez entrer une nouvelle race.")
            
        return "generation_fiche"  # Passe à la génération de la fiche

    @listen("start")
    def generer_fiche(self):
        """
        📌 Étape 2 : Génération de la fiche technique pour la race sélectionnée.

        🔹 `@listen(choisir_race)` signifie que cette étape **démarre automatiquement** 
           une fois que `choisir_race()` est terminée.
        🔹 Utilise `ChienCrew` pour produire une fiche descriptive.
        🔹 Ajoute une erreur volontaire pour tester la correction.
        🔹 Passe ensuite à `verifier_fiche()`, car elle est référencée dans `@router()`.
        """
        print("Génération de la fiche...")
        result = ChienCrew().crew().kickoff(inputs={"race": self.state.race})
        self.state.fiche = result.raw
        
        # Ajout d'une erreur intentionnelle pour tester la correction
        self.state.fiche += f" mais {self.state.race} est un chat !"
        
        print("Fiche générée :", self.state.fiche)

    @listen("corriger_fiche")
    def correction_fiche(self):
        """
        📌 Étape 4 : Correction de la fiche en cas d'erreurs.

        🔹 `@listen("corriger_fiche")` signifie que cette méthode est **appelée uniquement si**
           `verifier_fiche()` détecte des erreurs.
        🔹 Envoie la fiche incorrecte et la liste des erreurs à `FixCrew` pour correction.
        🔹 Après correction, renvoie la fiche vers `verifier_fiche()` pour une **nouvelle vérification**.
        """
        print("Correction de la fiche...")
        result = FixCrew().crew().kickoff(inputs={
            "race": self.state.race,
            "fiche": self.state.fiche,
            "list_error": self.state.list_error
        })

        self.state.fiche = result.raw
        print("Fiche corrigée :", self.state.fiche)

        return "verifier_fiche"  # Retourne à la vérification

    @router(or_(generer_fiche, correction_fiche))
    def verifier_fiche(self):
        """
        📌 Étape 3 : Vérification de la fiche générée.

        🔹 `@router()` permet de **déterminer dynamiquement la prochaine étape** en fonction du résultat.
        🔹 Ici, `verifier_fiche()` est appelée après **`generer_fiche()` ou `correction_fiche()`**.
        🔹 `VerifierCrew` analyse la fiche et renvoie un objet JSON contenant :
            - `good: True` si la fiche est correcte.
            - `good: False` avec une liste des erreurs détectées.
        🔹 Si des erreurs sont détectées, passe à `correction_fiche()`, sinon va à `save_fiche()`.
        """
        print("Vérification de la fiche...")
        result = VerifierCrew().crew().kickoff(inputs={"race": self.state.race, "fiche": self.state.fiche})
        
        if result.pydantic.good:
            print("✅ Fiche validée, passage à la sauvegarde.")
            return "save_fiche"
        else:
            print("❌ Erreurs détectées :", result.pydantic.list_error)
            self.state.list_error = result.pydantic.list_error
            return "corriger_fiche"
        
    @listen("save_fiche")
    def sauvegarder_fiche(self):
        """
        📌 Étape 5 : Sauvegarde de la fiche validée.

        🔹 `@listen("save_fiche")` signifie que cette méthode est **exécutée seulement si**
           `verifier_fiche()` valide la fiche comme correcte.
        🔹 Enregistre la fiche corrigée et validée dans un fichier JSON.
        """
        print("💾 Sauvegarde de la fiche...")
        with open("fiche_chien.json", "w", encoding="utf-8") as f:
            f.write(self.state.fiche)
        print("✅ Fiche sauvegardée avec succès.")


def kickoff():
    """
    Fonction principale pour démarrer le flow.

    🔹 Crée une instance de `ChienFlow` et lance l'exécution avec `.kickoff()`.
    🔹 Déclenche `choisir_race()` automatiquement grâce à `@start()`.
    """
    ChienFlow().kickoff()

def plot():
    chien_flow = ChienFlow()
    chien_flow.plot()

if __name__ == "__main__":
    kickoff()
