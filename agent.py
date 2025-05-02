# agent.py

import asyncio
import yaml
from core.loop import AgentLoop
from core.session import MultiMCP
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters
import os
import traceback  # Add this import for stack trace logging

def log(stage: str, msg: str):
    """Simple timestamped console logger."""
    import datetime
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

async def run_agent_with_input(user_input: str):
    """Run the agent with the provided user input."""
    print("🧠 Cortex-R Agent Ready")
    log("info", f"Processing query: {user_input}")

    # Load MCP server configs from profiles.yaml
    log("info", "Loading MCP server configs from profiles.yaml...")
    with open("config/profiles.yaml", "r") as f:
        profile = yaml.safe_load(f)
        mcp_servers = profile.get("mcp_servers", [])
    log("info", f"Loaded MCP servers: {mcp_servers}")

    multi_mcp = MultiMCP(server_configs=mcp_servers)
    log("info", "Initializing MultiMCP...")
    await multi_mcp.initialize()
    log("info", "MultiMCP initialized.")

    agent = AgentLoop(
        user_input=user_input,
        dispatcher=multi_mcp
    )
    log("info", "AgentLoop created. Starting agent.run()...")

    try:
        final_response = await agent.run()
        log("success", f"Final Answer: {final_response.replace('FINAL_ANSWER:', '').strip()}")
        return final_response
    except Exception as e:
        log("fatal", f"Agent failed: {e}")
        log("fatal", traceback.format_exc())  # Log the full stack trace
        raise

def handle_message(update: Update, context):
    """Handle incoming Telegram messages."""
    user_message = update.message.text
    log("info", f"Received message: {user_message}")
    try:
        asyncio.run(run_agent_with_input(user_message))
    except Exception as e:
        log("fatal", f"Error handling message: {e}")
        log("fatal", traceback.format_exc())

def main():
    """Start the Telegram bot and the agent."""
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    log("info", f"TELEGRAM_BOT_TOKEN loaded: {'Yes' if TELEGRAM_BOT_TOKEN else 'No'}")
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    log("info", "Bot started polling...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()