from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from groq import Groq
from dotenv import load_dotenv
import traceback
from fastapi.middleware.cors import CORSMiddleware

# This line reads your .env file at startup
load_dotenv()

# Use a relative import because we are inside a package
from . import database

# --- Application Setup ---
app = FastAPI(
    title="Text-to-SQL API",
    description="A fully dynamic API that converts natural language to SQL queries.",
    version="2.0.0",
)

# It tells the FastAPI server to trust requests coming from our React app.
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Pydantic Models ---
class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    sql_query: str
    data: list

# --- API Endpoints ---

@app.get("/health", tags=["Health Check"])
async def health_check():
    """A simple endpoint to confirm the API is running."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse, tags=["Text-to-SQL"])
async def ask_question(request: AskRequest):
    """
    Receives a natural language question, dynamically fetches the DB schema,
    converts the question to SQL, executes it, and returns the result.
    """
    print("\n--- [TEXT-TO-SQL] STEP 1: Received new question ---")
    try:
        # 1. Initialize Groq Client
        print("--- [TEXT-TO-SQL] STEP 2: Initializing Groq client... ---")
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        print("--- [TEXT-TO-SQL] SUCCESS: Groq client ready. ---")

        # 2. Get Database Schema Dynamically
        print("--- [TEXT-TO-SQL] STEP 3: Fetching dynamic DB schema... ---")
        db_schema = database.get_dynamic_schema()
        if not db_schema:
            raise HTTPException(status_code=500, detail="Could not retrieve database schema. Is the database empty?")
        print(f"--- [TEXT-TO-SQL] SUCCESS: Fetched schema:\n{db_schema} ---")

        # 3. Construct the NEW, MORE ROBUST prompt for the LLM
        print("--- [TEXT-TO-SQL] STEP 4: Building robust prompt for LLM... ---")
        prompt = f"""
        You are an expert PostgreSQL query writer. Your job is to write a SQL query based on the user's question and the database schema provided.

        **RULES:**
        1.  You **MUST ONLY** use the tables and columns provided in the schema. Do not guess or "hallucinate" columns.
        2.  You **MUST NOT** invent any table or column names. If a column from one table is mentioned, do not assume it exists in another table.
        3.  If the user's question cannot be answered using ONLY the provided schema, you MUST respond with the exact text: 'I cannot answer this question with the available data.'
        4.  Output ONLY the raw SQL query. No explanation, no markdown, no surrounding text.
        5.  Pay close attention to the exact column names and table names.
        
        **Schema:**
        {db_schema}

        **User Question:**
        {request.question}

        **SQL Query:**
        """

        # 4. Generate SQL query using Groq
        print("--- [TEXT-TO-SQL] STEP 5: Calling LLM to generate SQL... ---")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0,
        )
        sql_query = chat_completion.choices[0].message.content.strip()
        print(f"--- [TEXT-TO-SQL] SUCCESS: Generated SQL: {sql_query} ---")

        # 5. Execute the SQL query
        print("--- [TEXT-TO-SQL] STEP 6: Executing SQL query against database... ---")
        data = database.execute_query(sql_query)
        
        # --- FIX ADDED HERE ---
        # Handle cases where the query returns no results. The database function
        # might return None, which would cause a crash. We convert it to an empty list.
        if data is None:
            data = []

        print(f"--- [TEXT-TO-SQL] SUCCESS: Query executed. Found {len(data)} results. ---")

        # 6. Return the response
        return AskResponse(
            question=request.question,
            sql_query=sql_query,
            data=data,
        )
    except Exception as e:
        print(f"--- [TEXT-TO-SQL] FATAL ERROR in ask_question: {e} ---")
        traceback.print_exc()
        # It's better to return the actual error from the database if possible
        error_detail = str(e)
        if hasattr(e, 'pgerror'):
            error_detail = e.pgerror
        raise HTTPException(status_code=500, detail=f"Error executing SQL query: {error_detail}")
