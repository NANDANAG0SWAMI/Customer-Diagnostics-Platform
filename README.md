# Customer-Diagnostics-Platform



🚀 Customer Diagnostics Platform

A containerized, multi-service application featuring a React frontend and two intelligent FastAPI backends that use LLMs (Groq) for advanced data querying and diagnostics.

This platform provides a central UI to interact with two different microservices:

📚 The "Librarian": A dynamic Text-to-SQL API that can answer natural language questions about a database.

🕵️ The "Detective": A specialized Diagnostics API that runs multi-step investigations and saves processed reports.



🏛️ Architecture

This project runs a total of five containers managed by docker-compose.yml, creating a robust microservice architecture. An Nginx server within the frontend container acts as a reverse proxy, directing traffic to the correct backend service and eliminating CORS issues.

    User (Browser @ http://localhost:3000)
     │
     │
     ▼
    [Container: frontend (Nginx Reverse Proxy)]
     │
     ├─> [React UI]
     │
     ├─> /api/sql/* ───> [Container: text_to_sql_service (FastAPI:8000)] <──> [Container: text_to_sql_db (PostgreSQL)]
     │
     └─> /api/diag/* ───> [Container: diagnostics_service (FastAPI:8001)] <──> [Container: diagnostics_db (PostgreSQL)]
                           │
                           └──────(M2M API Call)─────> [text_to_sql_service (FastAPI:8000)]



🛠️ Tech Stack

Frontend: React (Vite), Tailwind CSS

Backend: FastAPI (Python), Groq (for LLM)

Databases: 2x PostgreSQL

Orchestration: Docker Compose

Web Server: Nginx (for serving React and as a reverse proxy)



✨ Key Features

🤖 Dynamic Text-to-SQL: The Librarian API connects to its database and uses introspection to build a schema on the fly. It's not hardcoded and will adapt to any tables you add to its init.sql script.

🧠 AI-Powered Diagnostics: The Detective API uses an LLM to generate a plan (a list of questions), then calls the Librarian API to execute that plan, and finally uses an LLM again to summarize the results.

🔄 M2M Communication: The diagnostics_service container makes real, authenticated machine-to-machine HTTP requests to the text_to_sql_service container.

🖥️ Multi-Page React UI: The frontend features a simple routing system with three pages: a Home/Landing page, the Text-to-SQL tool, and the Diagnostics tool.

🔌 Robust Networking: The Nginx reverse proxy solves all CORS (Cross-Origin Resource Sharing) issues, allowing a single, clean point of entry for the user.



🚀 How to Run This Project

Prerequisites

Docker Desktop (must be running)

A .env file in the project root

Step 1: 🛡️ (CRITICAL) Create Your Environment File

This project requires a .env file in the main Customer-diagnostics-platform/ directory to securely store your API key.

Create a file named .env.

Add your Groq API key to it:

    GROQ_API_KEY="gsk_YourSecretGroqApiKeyGoesHere"

Step 2: Ensure Data Scripts Exist

Make sure you have your data setup scripts in the correct folders:

./init-db/init.sql (for the Text-to-SQL database)

./init-db-diagnostics/init.sql (for the Diagnostics database)

Step 3: Nuke Old Data (Crucial for a Clean Start)

Before your first run, or any time you change the init.sql files, you must run this command. It destroys the old, cached database volumes and forces Docker to build fresh, clean databases from your scripts.

    docker compose down -v


Step 4: Build and Run

This single command will build all the container images and start the entire application.

    docker compose up --build


Step 5: Access Your Application

Once all containers are running, your application is live!

React Frontend: http://localhost:3000

Text-to-SQL API Docs: http://localhost:8000/docs

Diagnostics API Docs: http://localhost:8001/docs



📡 Available API Endpoints

📚 Librarian (Text-to-SQL) @ localhost:8000

GET /health: A simple health check.

POST /ask: Takes a JSON with a "question" and returns the SQL query and the data.

POST /add-customer: Takes a JSON with "first_name", "last_name", and "email" to add a new customer.




🕵️ Detective (Diagnostics) @ localhost:8001

POST /tools/diagnose-product: Takes a JSON with "product_id" and "product_name" and returns a full investigation report.
