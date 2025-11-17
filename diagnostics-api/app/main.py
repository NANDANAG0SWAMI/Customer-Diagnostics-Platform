from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# Import our custom modules
from . import tools
from . import database

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Diagnostics API",
    description="A service that runs automated diagnostic tools.",
    version="1.0.0",
)


origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Pydantic Models ---
class DiagnoseRequest(BaseModel):
    product_id: int
    product_name: str

# --- API Endpoints ---
@app.post("/tools/diagnose-product", tags=["Tools"])
async def run_product_diagnosis(request: DiagnoseRequest):
    """
    Triggers the product diagnosis tool, saves the result, 
    and returns the final report.
    """
    try:
        # 1. Run the actual "detective tool" from tools.py
        diagnosis_report = tools.diagnose_product_issues(
            product_id=request.product_id,
            product_name=request.product_name
        )

        if "error" in diagnosis_report:
            # If the tool itself returned an error, pass it along
            raise HTTPException(status_code=500, detail=diagnosis_report["error"])

        # 2. Save the successful diagnosis report to our own database
        database.save_diagnosis_result(
            product_id=diagnosis_report["product_id"],
            product_name=diagnosis_report["product_name"],
            summary=diagnosis_report["summary"],
            raw_data=diagnosis_report["raw_data"]
        )

        # 3. Return the report to the user
        return diagnosis_report

    except Exception as e:
        # This will catch any unexpected errors during the process
        print(f"An unexpected error occurred in the main endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")
