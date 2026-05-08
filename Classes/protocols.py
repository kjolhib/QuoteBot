import discord
from collections import deque
from typing import Protocol

from .song import Song

class MusicStateProtocol(Protocol):
  """
  Protocol to separate `MusicPlayer` and `GuildState`.
  """
  loop: bool
  current: Song | None
  voice_client: discord.VoiceClient | None
  queue: deque[Song]
  def q_to_embed(self) -> discord.Embed: ...
  async def clear_queue(self) -> None: ...

class ActiveViewProtocol(Protocol):
  """
  Protocol to handle views.
  """
  async def expire_cleanup(self, reason: str) -> None: ...
  async def edit_view(self, embed: discord.Embed, force_playing: bool = False) -> None: ...
