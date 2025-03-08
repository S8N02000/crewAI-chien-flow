from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel

class Response(BaseModel):
    Race: bool
    Message: str


@CrewBase
class CheckRaceCrew:
    # Fichiers de configuration contenant les définitions des agents et des tâches
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def verificateur_race(self) -> Agent:
        return Agent(
            config=self.agents_config["verificateur_race"],
        )

    @task
    def validation_race(self) -> Task:
        return Task(
            config=self.tasks_config["validation_race"],
            output_pydantic=Response  # La sortie doit être un objet Dog
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Liste des agents (générée automatiquement)
            tasks=[self.validation_race()],  # Liste des tâches initiales
            process=Process.sequential,  # Exécution séquentielle des tâches
            verbose=True,  # Affichage des logs d'exécution
            language="fr",
            full_output=True,
        )
