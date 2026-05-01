import discord
import datetime
from collections import deque
from typing import Optional, TYPE_CHECKING

from .dnd_session import DnDSession
from .dice import Dice
from exceptions.guild import missing_session_error
from exceptions.voice import clear_queue_error

# avoiding circular import
if TYPE_CHECKING:
  from .music_interaction import MusicInteractiveView

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
    self.active_view: Optional["MusicInteractiveView"] = None # the current view maintained by /queue command

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
  
  async def clear_queue(self):
    """
    Clears the queue.

    Sets current to `None` and `repeat` to False.
    """
    try:
      # Clear queue
      self.queue.clear()
      self.repeat = False

    except Exception:
      raise clear_queue_error.ClearQueueError(f"There was an error clearing the queue. Check logs for more details", "clear_queue", "somehow .clear() or .stop() failed")

  def q_to_embed(self) -> discord.Embed:
    embed = discord.Embed(title="Now Playing: ", description=f"**{self.current[1]}**" if self.current else "Nothing playing.")
    if self.queue:
      # Format the queue as:
      #   1. SongTitle 
      #   2. ...
      queue_str = "\n".join(f"`{i}`. {title}" for i, (_, title) in enumerate(self.queue, start=1))
      embed.add_field(name="Queue: ", value=queue_str, inline=False)

    # make it look nicer with the bottom 4 buttons
    embed.set_footer(text=f"Repeat: {'On' if self.repeat else 'Off'}\n{len(self.queue)} songs in queue.")
    return embed
  
  async def cleanup_voice(self):
    """
    Cleans up the voice client.

    Called whenever the queue is empty or /leave is called.
    """
    if self.voice_client:
      self.current = None
      await self.clear_queue()
      await self.voice_client.disconnect()
      await self.cleanup_view()

  async def cleanup_view(self):
    """
    Cleans up expired/disabled view.

    Will send a message and then disable all buttons.
    """
    if self.active_view:
      await self.active_view.expire_cleanup("*All songs have been played.*")
      self.active_view = None
