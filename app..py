from typing import Any
import json
import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

# Constantes Keycloak y API
KEYCLOAK_HOST = "app.tuenti.com.ar"
TOKEN_PATH = "/api/scale"

API_HOST = "api.tuenti.com.ar"
BALANCE_PATH = "/tuenti-fcd-balance/Balance"

# Valores fijos del payload
ANI = "541124048655"
USERTUENTI = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGQW91d3BiX1dCNllISVg2TWl5NFhBSkF3TDJxUVA4dzQyWXJ2UDZvRmU4In0.eyJleHAiOjE3NDQ0MDU2MTUsImlhdCI6MTc0NDQwNDcxNSwiYXV0aF90aW1lIjoxNzQ0NDA0NzE0LCJqdGkiOiI0Y2VmYzc0My0wODIzLTRkYjYtOTJkYS1hYmE3ZDc0NTY0NGIiLCJpc3MiOiJodHRwczovL3Nzby50dWVudGkuY29tLmFyL2F1dGgvcmVhbG1zL3R1ZW50aS1wcm9kIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjVlZTZlNmYwLWFkNjAtNGY4ZS04MzEwLWZiMmJiN2NlYjFhNCIsInR5cCI6IkJlYXJlciIsImF6cCI6InR1ZW50aS1wcm9kIiwibm9uY2UiOiI3OWExMmQzNS04OGZjLTQ0ZjItODNlMC00YWI5ZThlZDQ2YWEiLCJzZXNzaW9uX3N0YXRlIjoiMzFhOGYwZDMtMzdkYi00ZGVkLTk2ODQtODY4ZTlhOTA5OGQxIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2Rlc2EtdHVlbnRpLnNjaWRhdGEuY29tLmFyIiwiaHR0cHM6Ly9hcHAudHVlbnRpLmNvbS5hciIsImh0dHBzOi8vZm9yby50dWVudGkuY29tLmFyIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXR1ZW50aS1wcm9kIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJzaWQiOiIzMWE4ZjBkMy0zN2RiLTRkZWQtOTY4NC04NjhlOWE5MDk4ZDEiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmFtZSI6IkVEVUFSRE8gR1dJQVpEQSIsInByZWZlcnJlZF91c2VybmFtZSI6ImVkdWFyZG8uZ3dpYXpkYUB0ZWxlZm9uaWNhLmNvbSIsImdpdmVuX25hbWUiOiJFRFVBUkRPIiwidXNlcmlkIjoiNWVlNmU2ZjAtYWQ2MC00ZjhlLTgzMTAtZmIyYmI3Y2ViMWE0IiwiZmFtaWx5X25hbWUiOiJHV0lBWkRBIiwiZW1haWwiOiJlZHVhcmRvLmd3aWF6ZGFAdGVsZWZvbmljYS5jb20ifQ.ECG66ilxRVgVo9h24Ro7h3dO5F6-y-YSVbWl0IQyPdyAI8KvyELpS82RU7O2GTT3Lya1QYDuWFacfecr_ErdnCJIY_Qr5RbdC_gddrQQRh5Df2IPrfCyzuc2ordnJidwXXYouff6YR9z7uIHmBicNNOFBGE1UXkV36_RaDawBKmdet1HoSkLOGABohQ7KXM-xbCVJfH2R2H1aENqjImucHKZdtJs-h6czV5Rg0DXogLceGwUjA-ov7GtC__DoKZHVC4moyLFP2ag2dHyoh2bKvwMYfhM3fkcNf5JeLqko_vjy8FTYuHsUq6emfcwR29Ax9ZqQS4FgnvzeHGfFmDy2w"

@app.get("/get_balance")
async def get_balance():
    # Paso 1: Obtener token
    headers = { 'Referer': "https://app.tuenti.com.ar/get-balance/", 
               "Origin"  : "htps://apps.tuenti.com.ar" 
    }
    payload = ''
 
#
    async with httpx.AsyncClient(verify=True) as client:
        try:
            response = await client.post(f"https://{KEYCLOAK_HOST}{TOKEN_PATH}",
                                         timeout=15.0)
            print ("Status", response.status)
            response.raise_for_status()
            token = response.json().get("access_token")
        except Exception as e:
            print ("Exception",e)
            return JSONResponse(content={"error": f"Error al obtener token: {e}"})
   

    # Paso 2: Consultar balance
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Origin': 'https://app.tuenti.com.ar',
        'Referer': 'https://app.tuenti.com.ar',
        'user_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGQW91d3BiX1dCNllISVg2TWl5NFhBSkF3TDJxUVA4dzQyWXJ2UDZvRmU4In0...'
    }

    payload = {
        "ani": ANI,
        "Usertuenti": USERTUENTI
    }

    async with httpx.AsyncClient(verify=True) as client:
        try:
            response = await client.post(f"https://{API_HOST}{BALANCE_PATH}",
                                         json=payload, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            return JSONResponse(content={"saldo": data})
        except Exception as e:
            return JSONResponse(content={"error": f"Error al obtener balance: {e}"})

# MCP Plugin endpoints
@app.get("/.well-known/ai-plugin.json")
async def serve_plugin():
    return FileResponse(".well-known/ai-plugin.json", media_type="application/json")

@app.get("/openapi.json")
async def serve_openapi():
    return FileResponse("openapi.json", media_type="application/json")

# Comentario para que suba los fuentes

