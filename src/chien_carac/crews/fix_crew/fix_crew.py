from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from typing import List

class Dog(BaseModel):
    """
    Modèle de données représentant une fiche technique d'une race de chien.
    """
    race: str
    Features: str
    Disadvantages: str
    Education: str
    Food: str
    Care: str

@CrewBase
class FixCrew:
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
    def corriger_fiche_chien(self) -> Task:
        """
        Tâche : Corriger une fiche technique en fonction des erreurs détectées.
        Sortie structurée sous forme d'objet Pydantic `Dog`.
        """
        return Task(
            config=self.tasks_config["corriger_fiche_chien"],
            output_pydantic=Dog
        )

    @crew
    def crew(self) -> Crew:
        """
        Crée l'équipe de vérification des fiches techniques.
        """
        return Crew(
            agents=[self.expert_chien()],
            tasks=[self.corriger_fiche_chien()],
            process=Process.sequential,
            verbose=True,
            language="fr",
            full_output=True,
        )
