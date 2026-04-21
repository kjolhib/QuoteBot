import discord

from discord import app_commands
from classes.guild_state import GuildState

class QuoteBot(discord.Client):
  def __init__(self):
    intents = discord.Intents.default()
    intents.message_content = True
    super().__init__(intents=intents)
    self.tree = app_commands.CommandTree(self)
    self._guild_states: dict[str, GuildState] = {}

  def get_guild_state(self, guild_id: str) -> GuildState:
    if guild_id not in self._guild_states:
      self._guild_states[guild_id] = GuildState()
    return self._guild_states[guild_id]