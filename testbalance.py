import subprocess
import json
import asyncio

async def call_mcp_tool(tool_name: str, params: dict = None):
    process = await asyncio.create_subprocess_exec(
        "python", "mcptuenti.py",  # asumimos que tu código está guardado como mcp_server.py
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Mensaje para inicializar el protocolo MCP
    init_msg = {
        "type": "initialize",
        "client_id": "test-client",
        "message_id": 1,
    }

    process.stdin.write((json.dumps(init_msg) + "\n").encode())
    await process.stdin.drain()

    # Mensaje para invocar el tool
    invoke_msg = {
        "type": "invoke",
        "tool_name": tool_name,
        "input": params or {},
        "message_id": 2,
    }

    process.stdin.write((json.dumps(invoke_msg) + "\n").encode())
    await process.stdin.drain()

    # Leer respuestas
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        try:
            message = json.loads(line.decode())
            print(">>", json.dumps(message, indent=2))
            if message["type"] in ("tool_response", "error"):
                break
        except json.JSONDecodeError:
            continue

    await process.wait()

# Ejecutar
if __name__ == "__main__":
    asyncio.run(call_mcp_tool("get_balance"))
