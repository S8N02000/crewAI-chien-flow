import os
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource

def load_knowledge_sources():
    """
    📌 Charge automatiquement les fichiers de connaissance présents dans le dossier 'knowledge/'.

    🔹 Prend en charge plusieurs formats de fichiers : `.txt`, `.pdf`, `.csv`, `.xlsx`, `.json`.
    🔹 Vérifie si le dossier `knowledge` existe avant de tenter de charger des fichiers.
    🔹 Ajoute chaque fichier trouvé à une liste de sources de connaissance pour CrewAI.
    
    📂 Formats supportés :
    - `.txt` → Texte brut
    - `.pdf` → Documents PDF
    - `.csv` → Données tabulaires CSV
    - `.xlsx` → Feuilles de calcul Excel
    - `.json` → Données structurées JSON

    🔄 Retourne :
    - Une liste contenant des objets CrewAI KnowledgeSource correspondant aux fichiers chargés.
    """
    
    knowledge_sources = []
    knowledge_dir = "knowledge"  # Nom du dossier contenant les fichiers de connaissance

    print(f"\n📂 Dossier de travail actuel : {os.getcwd()}")  # 🔍 Affiche le chemin actuel
    print(f"📁 Vérification du dossier de connaissance : {knowledge_dir}")

    # Vérification de l'existence du dossier 'knowledge'
    if not os.path.exists(knowledge_dir):
        print("❌ Le dossier 'knowledge' n'existe pas ! Vérifie son emplacement.")
        return knowledge_sources

    print("\n📂 Détection des fichiers de connaissance...")

    # Parcours tous les fichiers du dossier 'knowledge'
    for file in os.listdir(knowledge_dir):
        file_path = os.path.join(knowledge_dir, file)  # Construction du chemin complet du fichier
        print(f"📄 Fichier détecté : {file}")

        # Vérification du type de fichier et création de l'objet correspondant
        if file.endswith(".txt"):
            knowledge_sources.append(TextFileKnowledgeSource(file_paths=[file_path]))
        elif file.endswith(".pdf"):
            knowledge_sources.append(PDFKnowledgeSource(file_paths=[file_path]))
        elif file.endswith(".csv"):
            knowledge_sources.append(CSVKnowledgeSource(file_paths=[file_path]))
        elif file.endswith(".xlsx"):
            knowledge_sources.append(ExcelKnowledgeSource(file_paths=[file_path]))
        elif file.endswith(".json"):
            knowledge_sources.append(JSONKnowledgeSource(file_paths=[file_path]))
        else:
            print(f"⚠️ Format non supporté : {file}")

        print(f"✅ Fichier chargé : {file}")

    # Vérification si des fichiers ont bien été chargés
    if not knowledge_sources:
        print("❌ Aucun fichier de connaissance valide trouvé !")
        
    return knowledge_sources