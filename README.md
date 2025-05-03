# Cortex-R Agent

A reasoning-driven AI agent capable of using external tools and memory to solve complex tasks step-by-step.  
Supports integration with Telegram, Gmail, and Google Drive/Sheets.

---

## Features

- **Multi-step Reasoning:** Uses LLMs to break down and solve user queries step by step.
- **Tool Integration:** Can call external tools via MCP servers (e.g., Gmail, Google Sheets, Web Search).
- **Telegram Bot Interface:** Interact with the agent via Telegram.
- **Google Sheets & Gmail Automation:** Create and share spreadsheets, send emails, and more.
- **Configurable Agent Profile:** Easily adjust agent behavior, memory, and tool settings via YAML.
- **Step-wise User Feedback:** Notifies users on Telegram at each major step of the workflow.

---

## Architecture Overview

```
Telegram
   |
[agent.py]  <--->  [core/loop.py]  <--->  [core/session.py]
   |                  |                        |
   |                  |                        |
[modules/*]      [core/context.py]         [MCP Servers]
   |                                         |
   |-------------------<---------------------|
```

- **agent.py:** Entry point, handles Telegram messages, runs the agent loop.
- **core/loop.py:** Main agent logic, step-wise reasoning, tool calls, and notifications.
- **core/session.py:** Manages connections to MCP servers for tool execution.
- **modules/**: Perception, memory, model management, and tool definitions.
- **config/**: YAML/JSON configuration for agent profile, models, and tool servers.

---

## Quickstart

### 1. **Clone the Repository**

```bash
git clone <your-repo-url>
cd <your-repo>
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```
or, if using `pyproject.toml`:
```bash
pip install .
```

### 3. **Configure Environment Variables**

Set up your `.env` file or export the following variables:

- `TELEGRAM_BOT_TOKEN` — Telegram bot token
- `GEMINI_API_KEY` — (if using Gemini LLM)
- `GOOGLE_CLIENT_SECRET_FILE` — Path to your Google API client secret JSON

### 4. **Configure Agent Profile and Tools**

Edit `config/profiles.yaml` to set up agent behavior and MCP tool servers (Gmail, Sheets, WebSearch, etc.).

### 5. **Run MCP Servers**

Start the required MCP servers for Gmail, Sheets, and WebSearch.  
Each server exposes tools via SSE endpoints (see `mcp_server_*.py`).

### 6. **Start the Agent**

```bash
python agent.py
```

---

## Usage

- **Interact via Telegram:**  
  Send a message to your bot (e.g.,  
  _"Find the Current Point Standings of F1 Racers, then put that into a Google Excel Sheet, and then share the link to this sheet with me (Your email id) on Gmail"_)

- **Step-wise Feedback:**  
  The bot will reply on Telegram at each major step:
  - Message received
  - Web search complete
  - Sheet created
  - Link emailed

---

## Configuration

### `config/profiles.yaml`

- **agent:** Name, ID, description
- **strategy:** Reasoning strategy and max steps
- **memory:** Memory settings (can be disabled if not needed)
- **llm:** LLM and embedding model selection
- **persona:** Tone and behavior
- **mcp_servers:** List of tool servers (Gmail, Sheets, WebSearch, etc.)

### `config/models.json`

- Model definitions for text generation and embeddings.

---

## Extending

- **Add new tools:** Implement in MCP server and register in `profiles.yaml`.
- **Change LLM:** Update `llm` section in `profiles.yaml` and `models.json`.
- **Customize notifications:** Edit notification logic in `core/loop.py` and `agent.py`.

---

## Troubleshooting

- **No response from tools:** Check MCP server logs and ensure they are running.
- **Google Sheets/Gmail issues:** Ensure valid credentials and correct API scopes.
- **Embedding errors:** Disable memory if not needed, or ensure embedding server is running.

---

## License

MIT

---

## Acknowledgements

- [python-telegram-bot](https://python-telegram-bot.org/)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Ollama](https://ollama.com/) (if using local LLM/embeddings)
