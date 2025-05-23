import streamlit as st
from openai import AzureOpenAI
import requests
import json
import time

# --- CONFIGURACION ---
client = AzureOpenAI(
    api_key="44wHfQGpGvl55Unrv3cMdihSQW31rzFKoikzhbSdOKphj5rAgRvAJQQJ99AKACfhMk5XJ3w3AAAAACOGEgii",
    api_version="2024-12-01-preview",
    azure_endpoint="https://ignac-m2ytusnj-swedencentral.cognitiveservices.azure.com"
)

assistant_id = "asst_zNwRQ8gl5bE2FDu0nkakSfjN"  # ID del Assistant creado en Foundry
#mcp_endpoint = "https://clouderswebpython.azurewebsites.net/get_balance"
mcp_endpoint = "http://localhost:8000/get_balance"
# --- STREAMLIT UI ---
st.set_page_config(page_title="Asistente Tuenti", page_icon="📱")
st.title("💬 Asistente Tuenti con Azure Assistant")

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    st.session_state.run_active = False
    st.session_state.messages = []

user_input = st.chat_input("Escribí tu consulta...")

if user_input and not st.session_state.run_active:
    st.session_state.messages.append({"role": "user", "content": user_input})

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    st.session_state.run_active = True
    thinking_placeholder = st.empty()
    thinking_placeholder.info("🤖 Pensando...")

    while True:
        print ("Rntro al run_status")
        run_status = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
        print ("Vuelvo del run  status")
        print ("status: ", run_status.status)
        if run_status.status in ["requires_action", "completed", "failed"]:
            break
        time.sleep(1)

    print ("run_status", run_status)
    # Procesar tool calls si las hay
    if run_status.status == "requires_action" and hasattr(run_status, "required_action"):
        tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
    
        for tool_call in tool_calls:
            if tool_call.function.name == "get_balance":
                try:
                    print ("Llamando al get_balance")
                    r = requests.get(mcp_endpoint, timeout=8)
                    saldo = r.json()
                    print ("saldo:", saldo)
                except Exception as e:
                    print ("Hubo un Error")
                    saldo = {"error": f"Error llamando al MCP: {e}"}

                tool_outputs.append({
                    "tool_call_id": getattr(tool_call, "id", ""),
                    "output": json.dumps(saldo)
                })

        print ("Voy a hacer un submit del tool_output");
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=st.session_state.thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

        while True:
            run_check = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            print ("run_check" ,run_check)
            if run_check.status == "completed":
                break
            time.sleep(1)

    st.session_state.run_active = False
    thinking_placeholder.empty()

    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    st.session_state.messages = [
        {"role": m.role, "content": m.content[0].text.value}
        for m in reversed(messages.data) if m.role in ["user", "assistant"]
    ]

# Mostrar historial del chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])