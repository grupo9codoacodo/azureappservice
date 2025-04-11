from typing import Any
import json
import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

# Constantes Keycloak y API
KEYCLOAK_HOST = "keycloak-tuenti-sso-service.apps.ocpprod.cuyorh.tcloud.ar"
TOKEN_PATH = "/auth/realms/tuenti-prod/protocol/openid-connect/token"
CLIENT_ID = "66321050"
CLIENT_SECRET = "626a9755e85776337f1973488c1b9ac9"

API_HOST = "api.tuenti.com.ar"
BALANCE_PATH = "/tuenti-fcd-balance/Balance"

# Valores fijos del payload
ANI = "541124048655"
USERTUENTI = "U2FsdGVkX1+nU4gDsXivQyLW5ut2qRzyB4PZBhlKvZntImHuXDe02Yl4BfX2iv57MtvbvUFHXithysd93amlSQ=="

@app.get("/get_balance")
async def get_balance():
    # Paso 1: Obtener token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(f"https://{KEYCLOAK_HOST}{TOKEN_PATH}",
                                         data=payload, headers=headers, timeout=15.0)
            response.raise_for_status()
            token = response.json().get("access_token")
        except Exception as e:
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

    async with httpx.AsyncClient(verify=False) as client:
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



