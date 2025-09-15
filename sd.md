You are tasked with porting a complex C# codebase into a simple Python FastAPI implementation. Follow these exact instructions:

1. Input

The source code is written in C#, uses OOP features like interfaces, inheritance, and ORM frameworks.

The repo contains two sample .csv files that represent fallback data sources.

2. Output Requirements

Generate a new folder named python_port/ inside the repo. Place all deliverables inside this folder:

app_sql.py → FastAPI app (Databricks via raw SQL, fallback to .csv).

app_orm.py → FastAPI app (Databricks via ORM, fallback to .csv).

api_docs.md → API endpoint documentation.

test_payloads.json → Example input requests and corresponding outputs.

test_api.py → Unit tests for all API endpoints.

Copy the .csv files from the repo into this folder so they can be used as fallback datasets.

3. Simplification Rules

Do not replicate the C# OOP design. Flatten logic into a single FastAPI file per version.

Keep things minimal and straightforward (no unnecessary abstractions).

Assume a minimal environment (no configs, no multiple modules).

Ignore Azure Function boilerplate — but ensure the code is compatible (plain FastAPI works fine in Azure Functions with ASGI).

4. Database Handling

Try Databricks first:

For SQL version, use raw SQL queries.

For ORM version, use SQLAlchemy or an equivalent ORM.

If Databricks connection fails:

Fall back to querying the .csv files (use pandas for data loading and querying).

Ensure the logic mirrors the same queries (filter, insert, etc.) but on CSV data.

5. Documentation

Generate api_docs.md containing:

List of all API endpoints.

Methods (GET, POST, PUT, DELETE).

Input parameters and response formats.

Example requests & responses.

6. Testing Deliverables

test_payloads.json → Include sample input payloads and expected outputs.

test_api.py → Write unit tests for the endpoints using pytest and httpx.AsyncClient.

7. Azure Functions Deployment

Do not add Azure Function bindings or decorators.

Simply confirm that .csv files can be committed and deployed as part of the repo (yes, they can — just ensure they are placed in the function app folder and accessed with relative paths).

8. Final Deliverables in python_port/

app_sql.py

app_orm.py

api_docs.md

test_payloads.json

test_api.py

data/ (folder containing the .csv files copied from the original repo)