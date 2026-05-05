import discord
import datetime
from collections import deque
from typing import Optional, TYPE_CHECKING

from .dnd_session import DnDSession
from .dice import Dice
from .song import Song
from exceptions.guild import missing_session_error
from exceptions.voice import clear_queue_error

# avoiding circular import
if TYPE_CHECKING:
  from .music_player import MusicPlayer

class GuildState:
  """
  Class to store the guild state of each guild where this bot is active.
  """
  def __init__(self):
    # DnD
    self.dnd_session : DnDSession | None = None # None initially

    # Music
    self.queue: deque[Song] = deque() # Queue of the songs
    """
    Format of the queue:
      {
        guild_id: deque([
          Song
        ])
      }
    """
    self.voice_client: discord.VoiceClient | None = None
    self.current: Song | None = None # current song, containing url, title
    self.repeat: bool = False # repeats current song
    self.active_view: Optional["MusicPlayer"] = None # the current view maintained by /queue command
    self.text_channel: discord.abc.Messageable | None = None # store the channel to send a message. distinct from safe_send since this applies to outside interactions, e.g. /repeat

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

    Sets `repeat` to False.

    Current song will play to completion, and will only stop if skipped or bot leaves.
    """
    try:
      # Clear queue
      self.queue.clear()
      self.repeat = False

    except Exception:
      raise clear_queue_error.ClearQueueError(f"There was an error clearing the queue. Check logs for more details", "clear_queue", "somehow .clear() or .stop() failed")

  def q_to_embed(self) -> discord.Embed:
    embed = discord.Embed(title="Now Playing: " if self.current else "Nothing playing.", description=f"**{self.current.title}** [{self.current.format_duration}]" if self.current else "")
    if self.queue:
      # Format the queue as:
      #   1. SongTitle 
      #   2. ...
      queue_str = "\n".join(f"`{i}`. {song.title} [{song.format_duration}]" for i, song in enumerate(self.queue, start=1))
      embed.add_field(name="Queue: ", value=queue_str, inline=False)

    # make it look nicer with the bottom 4 buttons
    embed.add_field(name="",value=f"Repeat: {'On' if self.repeat else 'Off'}\n{len(self.queue)} songs in queue.")
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
      await self.cleanup_view("Left the vc by command.")

  async def cleanup_view(self, reason: str = "*All songs have been played."):
    """
    Cleans up expired/disabled view.

    Will send a message and then disable all buttons.
    """
    if self.active_view:
      await self.active_view.expire_cleanup(reason)
      self.active_view = None

  async def send(self, message: str):
    """
    Sends a bot-initated message.

    This message is different to safe_send as it has no inherent `interaction` to reply to.

    Applicable to:
      `/play` used with `/repeat`. `play_next_song` requires this, as `/repeat` enabled would send a 
      message to the channel the `/play` command was invoked.

    Args:
      message: the message the bot sends to the channel
    """
    if self.text_channel:
      await self.text_channel.send(message)
    else:
      print(f"[GUILD_STATE]: send: cannot send message because text channel was None. Shouldn't be called.")
