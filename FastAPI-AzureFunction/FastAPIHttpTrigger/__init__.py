import azure.functions as func
from azure.functions import AsgiMiddleware
from function_app import app as fastapi_app

asgi_app = fastapi_app
main = func.AsgiFunctionApp(app=asgi_app)
