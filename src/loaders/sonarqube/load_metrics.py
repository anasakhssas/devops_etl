import os
import json
import psycopg2
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")))

# Chemin du fichier metrics du jour
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../../data/transformes/sonarqube/fact_project_metrics_" + 
                                            str(__import__('datetime').datetime.now().strftime("%Y%m%d")) + ".json"))

# Connexion à la base PostgreSQL avec les variables d'environnement
conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)
cur = conn.cursor()

# Création de la table des métriques si besoin
cur.execute("""
CREATE TABLE IF NOT EXISTS project_metrics (
    project_key TEXT,
    date_id INTEGER,
    branch_name TEXT,
    n_bugs INTEGER,
    n_vulnerabilities INTEGER,
    n_code_smells INTEGER,
    n_hotspots INTEGER,
    n_duplicated_lines FLOAT,
    coverage FLOAT,
    complexity INTEGER,
    n_lines_of_code INTEGER,
    extraction_date INTEGER
)
""")
conn.commit()

# Création de la table des projets du jour (avec contrainte d'unicité)
cur.execute("""
CREATE TABLE IF NOT EXISTS project_daily (
    project_key TEXT,
    project_name TEXT,
    language TEXT,
    visibility TEXT,
    created_at TEXT,
    date_id INTEGER,
    UNIQUE(project_key, date_id)
)
""")
conn.commit()

# Lecture du fichier JSON des métriques
with open(METRICS_FILE, "r", encoding="utf-8") as f:
    metrics = json.load(f)

# Lecture du fichier JSON des projets du jour
PROJECTS_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../../data/transformes/sonarqube/projects_simple.json"))
with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
    projects = json.load(f)

# Date du jour pour l'insertion
today_id = int(__import__('datetime').datetime.now().strftime("%Y%m%d"))

# Insertion des projets du jour sans doublons
for p in projects:
    cur.execute("""
        INSERT INTO project_daily (
            project_key, project_name, language, visibility, created_at, date_id
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (project_key, date_id) DO NOTHING
    """, (
        p["project_key"],
        p["project_name"],
        p.get("language"),
        p.get("visibility"),
        p.get("created_at"),
        today_id
    ))
conn.commit()

# Insertion des nouvelles métriques
for m in metrics:
    cur.execute("""
        INSERT INTO project_metrics (
            project_key, date_id, branch_name, n_bugs, n_vulnerabilities, n_code_smells,
            n_hotspots, n_duplicated_lines, coverage, complexity, n_lines_of_code, extraction_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        m["project_key"],
        m["date_id"],
        m["branch_name"],
        int(m["n_bugs"]),
        int(m["n_vulnerabilities"]),
        int(m["n_code_smells"]),
        int(m["n_hotspots"]),
        float(m["n_duplicated_lines"]),
        float(m["coverage"]),
        int(m["complexity"]),
        int(m["n_lines_of_code"]),
        m.get("extraction_date", m["date_id"])
    ))
conn.commit()

cur.close()
conn.close()
