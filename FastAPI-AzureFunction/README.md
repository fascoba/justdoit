# 🚀 FastAPI + Azure Function (Local Dev Template)

This is a minimal example of using **FastAPI** inside an **Azure Function**, including full support for OpenAPI docs (`/docs`) and local development with **no Azure account required**.

## 📦 Project Structure

```
FastAPI-AzureFunction/
├── FastAPIHttpTrigger/
│   ├── __init__.py         # Azure Function logic (ASGI)
│   └── function_app.py     # FastAPI routes
├── requirements.txt        # Python dependencies
├── host.json               # Azure Functions config
└── README.md               # Setup instructions
```

## ⚙️ Prerequisites

| Tool        | Version/Notes                     |
|-------------|-----------------------------------|
| Python      | 3.9 or 3.10 (recommended)         |
| Azure Functions Core Tools | v4+ (`func --version`) |
| Node.js     | Required for Azure Function Tools |
| pip         | Python package manager            |

Install Azure Functions Core Tools:
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

## 🛠 Setup Steps

### 1. Clone or unzip this project

```bash
cd FastAPI-AzureFunction
```

### 2. Create and activate a Python virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Azure Function locally

```bash
func start
```

## 🌐 Local Endpoints

| URL                             | Description          |
|----------------------------------|----------------------|
| `http://localhost:7071/api/`     | Hello world message  |
| `http://localhost:7071/api/hello/John` | Personalized greeting |
| `http://localhost:7071/api/docs` | Swagger UI (FastAPI) |
| `http://localhost:7071/api/redoc`| ReDoc UI (FastAPI)   |

## ✅ Next Steps

You can now:
- Modify `function_app.py` to add more routes
- Use full FastAPI features locally
- Deploy to Azure Functions when ready
