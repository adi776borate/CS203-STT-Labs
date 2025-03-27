from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import httpx
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Backend service URL
BACKEND_URL = "http://10.160.0.8:9567"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/get", response_class=HTMLResponse)
async def get_document(request: Request, query: str = Form(...)):
    try:
        # Forward the request to the backend service
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/search", json={"query": query})
            
        if response.status_code == 200:
            result = response.json()
        else:
            result = {"error": f"Backend service returned status code {response.status_code}"}
            
    except Exception as e:
        result = {"error": str(e)}
    
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

@app.post("/insert", response_class=HTMLResponse)
async def insert_document(request: Request, content: str = Form(...)):
    try:
        # Forward the request to the backend service
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_URL}/insert", json={"content": content})
            
        if response.status_code == 200:
            result = response.json()
        else:
            result = {"error": f"Backend service returned status code {response.status_code}"}
            
    except Exception as e:
        result = {"error": str(e)}
    
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

    # Run the FastAPI app with uvicorn on port 9567, binding to all addresses (0.0.0.0)
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9567,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )

