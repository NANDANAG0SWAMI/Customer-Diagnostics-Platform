import os
import psycopg2
from psycopg2.extras import DictCursor
import json # Moved import to the top for clarity

def get_db_connection():
    """Establishes a connection to the diagnostics database."""
    try:
        # --- FIX APPLIED HERE ---
        # Added the 'port' parameter to read the DB_PORT
        # environment variable from docker-compose.yml.
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            dbname=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            port=os.environ.get("DB_PORT") 
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"ERROR: Could not connect to the diagnostics database: {e}")
        raise

def save_diagnosis_result(product_id: int, product_name: str, summary: str, raw_data: dict):
    """
    Saves the result of a product diagnosis to the diagnosis_reports table.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            sql = """
                INSERT INTO diagnosis_reports (product_id, product_name, summary, raw_data)
                VALUES (%s, %s, %s, %s)
                RETURNING report_id;
            """
            # Convert raw_data dict to a JSON string to store in the database
            raw_data_json = json.dumps(raw_data)
            
            cur.execute(sql, (product_id, product_name, summary, raw_data_json))
            report_id = cur.fetchone()[0]
            conn.commit()
            print(f"Successfully saved diagnosis report with ID: {report_id}")
            return report_id
    except Exception as e:
        print(f"ERROR: Could not save diagnosis result to database: {e}")
        # If there's an error, roll back any changes
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
