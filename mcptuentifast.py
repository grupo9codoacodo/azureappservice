from typing import Any
import json
import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI()

# Constantes Keycloak y API
KEYCLOAK_HOST = "https://app.tuenti.com.ar"
TOKEN_PATH = "/api/scale"
CLIENT_ID = "66321050"
CLIENT_SECRET = "626a9755e85776337f1973488c1b9ac9"

API_HOST = "api.tuenti.com.ar"
BALANCE_PATH = "/tuenti-fcd-balance/Balance"

# Valores fijos del payload
ANI = "541124048655"
USERTUENTI = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGQW91d3BiX1dCNllISVg2TWl5NFhBSkF3TDJxUVA4dzQyWXJ2UDZvRmU4In0.eyJleHAiOjE3NDQzOTk3OTEsImlhdCI6MTc0NDM5ODg5MSwiYXV0aF90aW1lIjoxNzQ0Mzk4ODkxLCJqdGkiOiJjNDEwNjcxMy1mOTJjLTRmZTktYTMwMi01NGFkNzI3MTA2MDgiLCJpc3MiOiJodHRwczovL3Nzby50dWVudGkuY29tLmFyL2F1dGgvcmVhbG1zL3R1ZW50aS1wcm9kIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjVlZTZlNmYwLWFkNjAtNGY4ZS04MzEwLWZiMmJiN2NlYjFhNCIsInR5cCI6IkJlYXJlciIsImF6cCI6InR1ZW50aS1wcm9kIiwibm9uY2UiOiIxYWZlODAzMS05ZTU5LTQzM2UtOTJmYy0xMjZjMWNhY2U3ODAiLCJzZXNzaW9uX3N0YXRlIjoiNmJlOWI0MDYtYmZiNi00MDA3LWI3NTUtNWQwNzA5MTJkOTM0IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2Rlc2EtdHVlbnRpLnNjaWRhdGEuY29tLmFyIiwiaHR0cHM6Ly9hcHAudHVlbnRpLmNvbS5hciIsImh0dHBzOi8vZm9yby50dWVudGkuY29tLmFyIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXR1ZW50aS1wcm9kIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJzaWQiOiI2YmU5YjQwNi1iZmI2LTQwMDctYjc1NS01ZDA3MDkxMmQ5MzQiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmFtZSI6IkVEVUFSRE8gR1dJQVpEQSIsInByZWZlcnJlZF91c2VybmFtZSI6ImVkdWFyZG8uZ3dpYXpkYUB0ZWxlZm9uaWNhLmNvbSIsImdpdmVuX25hbWUiOiJFRFVBUkRPIiwidXNlcmlkIjoiNWVlNmU2ZjAtYWQ2MC00ZjhlLTgzMTAtZmIyYmI3Y2ViMWE0IiwiZmFtaWx5X25hbWUiOiJHV0lBWkRBIiwiZW1haWwiOiJlZHVhcmRvLmd3aWF6ZGFAdGVsZWZvbmljYS5jb20ifQ.ZmMrbQeivLpXLVnNZ9wYS3U538raY_DAAXJQ0fej8xWOhEpWZO0z1POXGHxleAMz2vKqCz6uvId7eQZ6hgGZBf3AGsuQ2AJycZ5kKnRNR8TI_gF8JO_tBgvBkKV206IyLqxv4UuqJJOARUn_U_RG1QExg8p2FE8rZ0dWC5lv3BSKOo0gVchZGNr0CozSQJPYtq22Hk5vkBxC7w9LsJpqM8bnKDTFfho5PBE9ortEYAzGfNkfE0BEpkdPUsw2-5yvZ65qki2_l5SG4H8-4j1XvPyfpnRx3gohFtON-P10LbBUX4z-BHEFrR00BFhQP9DqUgH7g1o94LOQVQDJsGuEbQ"

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



