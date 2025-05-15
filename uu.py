__init__.py


import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')

    if req.method == "GET":
        return func.HttpResponse(
            "This is a GET request",
            status_code=200
        )

    elif req.method == "POST":
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON in request body",
                status_code=400
            )
        
        return func.HttpResponse(
            json.dumps(req_body),
            mimetype="application/json",
            status_code=200
        )

    else:
        return func.HttpResponse(
            "Method not allowed",
            status_code=405
        )






 # function.json

{
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get", "post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}


# GET /api/your-function-name


HttpEchoFunctionApp/              # Root directory (your Function App name)
│
├── HttpEcho/                    # Your function folder (can be any name)
│   ├── __init__.py              # Function logic (Python entry point)
│   ├── function.json            # Function bindings and settings
│
├── host.json                    # Global configuration for all functions
├── local.settings.json          # Local development settings (only used locally)
├── requirements.txt             # Python dependencies



my_project/
├── app/
│   ├── __init__.py         # You can put shared logic here
│   └── config.ini          # Custom config file
├── function_app.py         # Main shared logic or setup (not the entry point in Azure Functions)
├── HttpEcho/               # Azure Function directory
│   ├── __init__.py         # Actual Azure Function code (will import from app or function_app.py)
│   ├── function.json       # Required for Azure Function
├── requirements.txt
├── host.json
├── local.settings.json




# HttpEcho/__init__.py

import logging
import azure.functions as func
import json

from function_app import handle_request  # import from top-level file

def main(req: func.HttpRequest) -> func.HttpResponse:
    return handle_request(req)


# function_app.py
import json
import azure.functions as func

def handle_request(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        return func.HttpResponse("This is a GET request", status_code=200)

    elif req.method == "POST":
        try:
            data = req.get_json()
            return func.HttpResponse(json.dumps(data), mimetype="application/json", status_code=200)
        except ValueError:
            return func.HttpResponse("Invalid JSON", status_code=400)

    else:
        return func.HttpResponse("Method not allowed", status_code=405)


















