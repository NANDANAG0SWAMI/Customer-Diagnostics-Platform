import os
import httpx
import json
from groq import Groq
import time
import traceback

# --- Configuration ---
# --- FIX APPLIED HERE ---
# Instead of hardcoding the URL, we read it from the environment variable
# set in docker-compose.yml. This makes the code flexible.
TEXT_TO_SQL_API_URL = os.environ.get("TEXT_TO_SQL_API_URL")
if not TEXT_TO_SQL_API_URL:
    print("--- [DIAGNOSTICS] FATAL: TEXT_TO_SQL_API_URL environment variable not set. ---")
    # Set a fallback, but this should always be provided by docker-compose.
    TEXT_TO_SQL_API_URL = "http://text_to_sql_service:8000/ask"


# --- Main Tool Function ---

def diagnose_product_issues(product_id: int, product_name: str):
    """
    This is our main "Detective" tool. It investigates product issues dynamically.
    """
    print(f"\n--- [DIAGNOSTICS] STEP 1: Starting diagnosis for product: {product_name} (ID: {product_id}) ---")
    try:
        # 1. Generate investigatory questions
        print("\n--- [DIAGNOSTICS] STEP 2: Generating investigatory questions from Groq... ---")
        questions_to_ask = _get_investigatory_questions(product_name)
        if not questions_to_ask:
            print("--- [DIAGNOSTICS] ERROR: Failed to generate questions. Aborting. ---")
            return {"error": "Could not generate investigatory questions from the AI."}
        print(f"--- [DIAGNOSTICS] SUCCESS: Generated {len(questions_to_ask)} questions: {questions_to_ask} ---")

        # 2. Answer each question using Text-to-SQL service
        print("\n--- [DIAGNOSTICS] STEP 3: Fetching data from Text-to-SQL service... ---")
        raw_data = {}
        for question in questions_to_ask:
            print(f"--- [DIAGNOSTICS] Sub-step: Asking '{question}' ---")
            data = _fetch_data_from_text_to_sql_api(question)
            raw_data[question] = data
            print(f"--- [DIAGNOSTICS] Sub-step: Received data: {json.dumps(data, indent=2)} ---")

        # 3. Create a final summary
        print("\n--- [DIAGNOSTICS] STEP 4: Creating summary from collected data... ---")
        summary = _create_summary_from_data(product_name, raw_data)
        print(f"--- [DIAGNOSTICS] SUCCESS: Generated summary. ---")

        final_report = {
            "product_id": product_id,
            "product_name": product_name,
            "summary": summary,
            "raw_data": raw_data
        }
        print("\n--- [DIAGNOSTICS] STEP 5: Diagnosis complete. Final report generated. ---")
        return final_report

    except Exception as e:
        print(f"--- [DIAGNOSTICS] FATAL ERROR in diagnose_product_issues: {e} ---")
        traceback.print_exc()
        return {"error": f"An unexpected fatal error occurred during diagnosis: {e}"}


# --- Helper Functions (with added logging) ---

def _get_investigatory_questions(product_name: str) -> list[str]:
    """Uses Groq to generate a list of questions to ask about a product."""
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        prompt = f"""
        You are a diagnostics expert. A customer is having issues with a product called "{product_name}".
        Based on a database containing tables for 'customers', 'products', and 'support_tickets',
        generate a JSON list of 3 specific, useful questions you would ask the database to investigate the problem.
        The questions should be simple, natural language.
        
        Example format:
        ["What are the most recent support tickets for this product?", "Which customers have open tickets for this product?"]
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        
        if not chat_completion.choices:
            print("--- [DIAGNOSTICS] HELPER ERROR: Groq API returned an empty 'choices' list for questions.")
            return []

        response_text = chat_completion.choices[0].message.content
        response_data = json.loads(response_text)
        
        if isinstance(response_data, list):
            return response_data
        for key, value in response_data.items():
            if isinstance(value, list):
                return value
        return []
    except Exception as e:
        print(f"--- [DIAGNOSTICS] HELPER ERROR in _get_investigatory_questions: {e}")
        traceback.print_exc()
        return []

def _fetch_data_from_text_to_sql_api(question: str, max_retries: int = 3, delay: int = 2):
    """Makes an M2M call to our Text-to-SQL API with a retry mechanism."""
    for attempt in range(max_retries):
        try:
            response = httpx.post(TEXT_TO_SQL_API_URL, json={"question": question}, timeout=30.0)
            response.raise_for_status()
            return response.json().get("data", [])
        except httpx.RequestError as e:
            print(f"--- [DIAGNTICS] M2M ATTEMPT {attempt + 1}/{max_retries} FAILED: Could not connect. Retrying... Error: {e}")
            time.sleep(delay)
    print(f"--- [DIAGNOSTICS] M2M FATAL: Failed to get data after {max_retries} attempts.")
    return {"error": f"Failed to get data from Text-to-SQL API after {max_retries} attempts."}

def _create_summary_from_data(product_name: str, raw_data: dict) -> str:
    """Uses Groq to generate a final summary from the collected data."""
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        data_string = json.dumps(raw_data, indent=2)

        prompt = f"""
        You are a diagnostics expert investigating "{product_name}".
        You have gathered the following data:
        ---
        {data_string}
        ---
        Based ONLY on the data provided, write a brief, one-paragraph summary of the situation.
        If there are support tickets, mention the common themes. If no data, state that.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.1,
        )
        
        if not chat_completion.choices:
            print("--- [DIAGNOSTICS] HELPER ERROR: Groq API returned an empty 'choices' list for summary.")
            return "Could not generate summary because the AI returned an empty response."

        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"--- [DIAGNOSTICS] HELPER ERROR in _create_summary_from_data: {e}")
        traceback.print_exc()
        return "Could not generate a summary due to an error."
