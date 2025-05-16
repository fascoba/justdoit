import azure.functions as func

from WrapperFunction import app as fastapi_app

print("ASGI Function initialized")

app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)