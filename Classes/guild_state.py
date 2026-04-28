import discord
import datetime
from collections import deque

from .dnd_session import DnDSession
from .dice import Dice
from exceptions.guild import missing_session_error

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

  def start(self, time: float, dice: list[Dice] = []):
    """
    Starts the dnd session.
    
    Initialises a dnd_session class with a given timestamp.
    """
    self.dnd_session = DnDSession(True, time, dice)

  def end(self):
    """
    Ends a dnd session.

    Should only be called if a DnDSession is already active.
    """
    # How long the session lasted
    if not self.dnd_session:
      raise missing_session_error.MissingSessionError(f"A fatal error occurred when trying to end this session: the session **doesn't** exist! Check logs, @chewswisely *really* fucked something up.", "end", "/end called successfully with the require_dnd_session decorator failing to capture the none state of the dnd session. As a result, /end called with a None dnd_session")
    end_time = discord.utils.utcnow().timestamp()
    assert self.dnd_session.start_time
    duration = end_time - self.dnd_session.start_time
    human_readable_time = str(datetime.timedelta(seconds=duration))
    
    # Clear session
    self.dnd_session = None
    return human_readable_time
