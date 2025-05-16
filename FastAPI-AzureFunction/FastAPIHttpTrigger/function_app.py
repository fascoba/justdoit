from fastapi import FastAPI

app = FastAPI(
    title="FastAPI on Azure Functions",
    description="Using FastAPI docs with Azure Functions",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI"}

@app.get("/hello/{name}")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}
