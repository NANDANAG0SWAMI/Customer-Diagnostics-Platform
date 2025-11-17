# Customer-Diagnostics-Platform
A multi-container Customer Diagnostics Platform (React/Docker) with two AI services. The "Librarian" is a Text-to-SQL API (Groq LLM) that answers natural language questions from any PostgreSQL DB. The "Detective" API uses the Librarian (M2M) to conduct multi-step investigations and generate summarized reports. A robust microservice architecture.
