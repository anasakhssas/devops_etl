import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement depuis le fichier .env

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
            dbname=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD")
        )
        return conn
    except Exception as e:
        print(f"[❌] Erreur lors de la connexion à la base de données : {e}")
        raise
