import asyncio
import discord
import os
from dotenv import load_dotenv
from typing import Any

from QuoteBot import get_env

"""
Usage: python3 clear_commands.py

This file will clear and effectively refresh the commands cached on a server.
"""
load_dotenv()

BOT_TOKEN = os.getenv("QBOT_TOKEN")
if not BOT_TOKEN:
  raise ValueError("clear_commands: Bot token is null or invalid.")
GUILD_IDS = [
  get_env("DEV_SERVER"),
  get_env("GHIONCK")
]

async def clear():
  client = discord.Client(intents=discord.Intents.default())
  tree = discord.app_commands.CommandTree(client)

  @client.event
  async def on_ready(): # type: ignore
    tasks: Any = []
    for g in GUILD_IDS:
      guild = discord.Object(id=g)
      tree.clear_commands(guild=guild)
      tasks.append(tree.sync(guild=guild))
      print(f"Cleared commands from guild {g}")
    
    # do all tasks at once
    await asyncio.gather(*tasks)
    await client.close()

  await client.start(BOT_TOKEN) # type: ignore

asyncio.run(clear())
