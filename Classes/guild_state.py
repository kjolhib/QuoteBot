import discord
from .dnd_session import DnDSession
from collections import deque

class GuildState:
  """
  Class to store the guild state of each guild where this bot is active.
  """
  def __init__(self):
    # DnD
    self.dnd_session : DnDSession | None = None # None initially

    # Music
    self.queue: deque[tuple[str, str]] = deque() # Queue of the songs
    """
    Format of the queue:
      {
        guild_id: deque([
          (youtube link: string, title: string),
          ...
        ])
      }
    """
    self.voice_client: discord.VoiceClient | None = None
    self.current: tuple[str, str] | None = None # current song, containing url, title
    self.repeat: bool = False # repeats current song

