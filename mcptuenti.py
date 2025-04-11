from typing import Any
import json
import httpx
from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP server
mcp = FastMCP("balance-checker")

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

async def get_token() -> str | None:
    """Obtiene el token de Keycloak."""
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
            token_data = response.json()
            return token_data.get("access_token")
        except Exception as e:
            return f"Error al obtener token: {e}"

@mcp.tool()
async def get_balance() -> str:
    """Consulta el saldo de tuenti ."""
    token = await get_token()
    if not token or "Error" in token:
        return str(token)  # Error message

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Origin': 'https://app.tuenti.com.ar',
        'Referer': 'https://app.tuenti.com.ar',
        'user_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGQW91d3BiX1dCNllISVg2TWl5NFhBSkF3TDJxUVA4dzQyWXJ2UDZvRmU4In0.eyJleHAiOjE3NDQyODc0OTUsImlhdCI6MTc0NDI4NjU5NSwiYXV0aF90aW1lIjoxNzQ0Mjg2NTk1LCJqdGkiOiJiOWVmNDE2ZS02ZmY1LTRmOWEtOTM2ZC0zOTc3NmJjMTgzODEiLCJpc3MiOiJodHRwczovL3Nzby50dWVudGkuY29tLmFyL2F1dGgvcmVhbG1zL3R1ZW50aS1wcm9kIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjVlZTZlNmYwLWFkNjAtNGY4ZS04MzEwLWZiMmJiN2NlYjFhNCIsInR5cCI6IkJlYXJlciIsImF6cCI6InR1ZW50aS1wcm9kIiwibm9uY2UiOiIxYmFmYTJjMC0wZmNjLTRmZjEtODg3NS1lMDdjMTUyODc3MzIiLCJzZXNzaW9uX3N0YXRlIjoiNGUwMTMzZjgtOWZhNC00NzNiLWE1YzYtODFlZDk0NTU2YmQ3IiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL2Rlc2EtdHVlbnRpLnNjaWRhdGEuY29tLmFyIiwiaHR0cHM6Ly9hcHAudHVlbnRpLmNvbS5hciIsImh0dHBzOi8vZm9yby50dWVudGkuY29tLmFyIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXR1ZW50aS1wcm9kIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwiLCJzaWQiOiI0ZTAxMzNmOC05ZmE0LTQ3M2ItYTVjNi04MWVkOTQ1NTZiZDciLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmFtZSI6IkVEVUFSRE8gR1dJQVpEQSIsInByZWZlcnJlZF91c2VybmFtZSI6ImVkdWFyZG8uZ3dpYXpkYUB0ZWxlZm9uaWNhLmNvbSIsImdpdmVuX25hbWUiOiJFRFVBUkRPIiwidXNlcmlkIjoiNWVlNmU2ZjAtYWQ2MC00ZjhlLTgzMTAtZmIyYmI3Y2ViMWE0IiwiZmFtaWx5X25hbWUiOiJHV0lBWkRBIiwiZW1haWwiOiJlZHVhcmRvLmd3aWF6ZGFAdGVsZWZvbmljYS5jb20ifQ.PlrOO0HW1gdB5iSfYMgejYTULKysew5Ghj9wWPlCMzoBBkVybG1RDDFWXAHjDzB-1xTQHwvb6-ZeIPnN6lL3eG_OHEi8t6_TLzSFjf-xcMk99yidZhw1sXrHhCpBMxWRyNrJSWAlesImS0CvNo1juA5DE7JQ5Zhqcwy-u551Bn4Yc2wCI_s7wP92WmJuu7MjgL0fpyHHgRnvuYls92dyhhxwu7WSXV0HRKZd2_LNGksr_iYEW85s7ZN5ucT0EXcExW4KeZx9zIfodzCptp9TE_YGsgO5e2jdaC0MTeZCnM7HlHuAjCCCctFJ2C68VT-kr3x00EtfJnEuPfnwtOWocw'
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
            #amount = data.get("Amount", "Monto no encontrado en la respuesta.")
            return f"El saldo actual es: {data}"
        except Exception as e:
            return f"Error al obtener balance: {e}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
