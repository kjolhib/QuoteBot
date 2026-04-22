import asyncio
import discord
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("QBOT_TOKEN")
if not BOT_TOKEN:
  raise ValueError("clear_commands: Bot token is null or invalid.")
GUILD_ID = int(os.getenv("DEV_SERVER"))
if not GUILD_ID:
  raise ValueError("clear_commands: guild to clear commands is null or invalid.")

async def clear():
  client = discord.Client(intents=discord.Intents.default())
  tree = discord.app_commands.CommandTree(client)

  @client.event
  async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    tree.clear_commands(guild=guild)
    await tree.sync(guild=guild)
    print(f"Cleared commands from guild {GUILD_ID}")
    await client.close()

  await client.start(BOT_TOKEN)

asyncio.run(clear())
