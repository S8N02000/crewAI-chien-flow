from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from typing import List

class Verif(BaseModel):
    """
    Modèle de données représentant le résultat de la vérification d'une fiche.
    """
    good: bool  # True si la fiche est correcte, False sinon
    list_error: List[str]  # Liste des erreurs détectées


@CrewBase
class VerifierCrew:
    """
    VérifierCrew est une équipe chargée d'analyser une fiche technique de chien
    et de signaler les erreurs éventuelles.
    """
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def expert_chien(self) -> Agent:
        """
        Crée un agent expert en dressage canin pour vérifier les fiches.
        """
        return Agent(
            config=self.agents_config["expert_chien"],
        )

    @task
    def verifier_fiche_chien(self) -> Task:
        """
        Tâche : Vérifier la fiche technique et identifier les erreurs.
        Sortie structurée sous forme d'objet Pydantic `Verif`.
        """
        return Task(
            config=self.tasks_config["verifier_fiche_chien"],
            agent=self.expert_chien(),
            output_pydantic=Verif
        )

    @crew
    def crew(self) -> Crew:
        """
        Crée l'équipe de vérification des fiches techniques.
        """
        return Crew(
            agents=[self.expert_chien()],
            tasks=[self.verifier_fiche_chien()],
            process=Process.sequential,
            verbose=True,
            language="fr",
            full_output=True,
        )
