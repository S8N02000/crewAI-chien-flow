from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from chien_carac.knowledge_loader import load_knowledge_sources

class Dog(BaseModel):
    """
    Modèle de données représentant une fiche technique d'une race de chien.
    """
    Race: str
    Features: str
    Disadvantages: str
    Education: str
    Food: str
    Care: str


@CrewBase
class ChienCrew:
    """
    ChienCrew est une équipe qui génère et corrige des fiches techniques
    sur différentes races de chiens.
    """
    # Fichiers de configuration contenant les définitions des agents et des tâches
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def expert_chien(self) -> Agent:
        """
        Crée un agent expert en dressage canin.
        Cet agent est chargé de générer et corriger les fiches techniques.
        """
        return Agent(
            config=self.agents_config["expert_chien"],
        )

    @task
    def generer_fiche_chien(self) -> Task:
        """
        Tâche : Générer une fiche technique détaillée d'une race de chien.
        Sortie structurée sous forme d'objet Pydantic `Dog`.
        """
        return Task(
            config=self.tasks_config["description_chien"],
            output_pydantic=Dog  # La sortie doit être un objet Dog
        )

    @crew
    def crew(self) -> Crew:
        """
        Crée une équipe d'agents spécialisés dans la génération de fiches
        techniques de races de chiens.
        """
        return Crew(
            agents=self.agents,  # Liste des agents (générée automatiquement)
            tasks=[self.generer_fiche_chien()],  # Liste des tâches initiales
            process=Process.sequential,  # Exécution séquentielle des tâches
            verbose=True,  # Affichage des logs d'exécution
            language="fr",
            full_output=True,
            knowledge_sources=load_knowledge_sources(),
            embedder={
                "provider": "ollama",
                "config": {"model": "nomic-embed-text"}  # Modèle d'embedding utilisé par Ollama
            }
        )
