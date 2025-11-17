import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

# --- Database Connection ---

# This function establishes a connection to the PostgreSQL database.
# It includes a retry mechanism to handle initial connection delays.
def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    retries = 5
    while retries > 0:
        try:
            # --- FIX APPLIED HERE ---
            # The environment variable names now match the ones provided in docker-compose.yml
            # (e.g., DB_NAME instead of POSTGRES_DB)
            conn = psycopg2.connect(
                dbname=os.environ.get("DB_NAME"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASSWORD"),
                host=os.environ.get("DB_HOST"), # This will be 'text_to_sql_db' from docker-compose
                port=os.environ.get("DB_PORT")  # This will be '5432' from docker-compose
            )
            print("--- [DATABASE] SUCCESS: Connected to PostgreSQL. ---")
            return conn
        except psycopg2.OperationalError as e:
            print(f"--- [DATABASE] ERROR: Could not connect to database. Retrying... ({retries} attempts left) ---")
            print(f"--- [DATABASE] Details: {e} ---")
            retries -= 1
            time.sleep(5) # Wait for 5 seconds before retrying
    return None

# --- Query Execution ---

# This is the function where the original error was happening.
def execute_query(sql_query: str):
    """
    Executes a SQL query against the database and returns the results.
    Handles potential errors and ensures a list is always returned.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("--- [DATABASE] FATAL: Failed to establish database connection. ---")
            return None # Return None if connection fails completely

        # Use RealDictCursor to get results as a list of dictionaries
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_query)
            
            # THE FIX IS HERE:
            # We check if the query will return results before trying to fetch them.
            # SELECT, WITH, and some other statements have a `description`.
            if cur.description:
                results = cur.fetchall()
                # fetchall() returns an empty list [] if no rows are found, which is perfect.
                return results
            else:
                # This handles non-returning statements like INSERT, UPDATE, DELETE
                conn.commit()
                return [{"status": "success", "rows_affected": cur.rowcount}]

    except psycopg2.Error as e:
        print(f"--- [DATABASE] SQL Execution Error: {e} ---")
        # In case of an error, it's safer to return None or re-raise
        # the exception to be handled by the main API endpoint.
        # We re-raise it to provide detailed error info to the user.
        raise e

    finally:
        if conn:
            conn.close()

# --- Schema Introspection ---

def get_dynamic_schema():
    """
    Dynamically introspects the database to get table and column information.
    """
    query = """
    SELECT
        c.table_name,
        c.column_name,
        c.data_type
    FROM
        information_schema.columns c
    WHERE
        c.table_schema = 'public'
    ORDER BY
        c.table_name,
        c.ordinal_position;
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            columns_info = cur.fetchall()

        if not columns_info:
            return None

        # Format the schema into a readable string for the LLM prompt
        schema_str = ""
        current_table = ""
        for col in columns_info:
            if col['table_name'] != current_table:
                current_table = col['table_name']
                schema_str += f"\nTable: {current_table}\n"
            schema_str += f"  - {col['column_name']} ({col['data_type']})\n"

        return schema_str.strip()

    except psycopg2.Error as e:
        print(f"--- [DATABASE] Schema Fetch Error: {e} ---")
        return None
    finally:
        if conn:
            conn.close()
