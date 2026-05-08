import discord
import datetime
from collections import deque

from .dnd_session import DnDSession
from .dice import Dice
from .song import Song
from .protocols import ActiveViewProtocol
from exceptions.guild import missing_session_error
from exceptions.voice import clear_queue_error

class GuildState:
  """
  Class to store the guild state of each guild where this bot is active.

  Attributes:
    `dnd_session`: stores the class DnDSession. `None` if not initialised.
    `queue`: stores the songs in a list. Initialised as an empty queue.
    `voice_client`: stores whether or not the bot in this guild is connected to a voice chat.
    `current`: the currently playing song, in the class Song.
    `repeat`: whether or not this bot is on repeat.
    `active_view`: the current view that is maintained by the `/queue` command.
    `text_channel`: stores information about the text channel in which a command was sent, that requires continued messaging exceeding the 15 mins interaction token expiration.
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
    self.current: Song | None = None
    self.loop: bool = False
    self.active_view: ActiveViewProtocol | None = None
    self.text_channel: discord.abc.Messageable | None = None # store the channel to send a message. distinct from safe_send since this applies to outside interactions, e.g. /repeat

  def start(self, time: float, dice: list[Dice] = []) -> None:
    """
    Starts the dnd session.
    
    Initialises a `DnDSession` class.
    """
    self.dnd_session = DnDSession(True, time, dice)

  def end(self) -> str:
    """
    Ends a dnd session.

    Should only be called if a `DnDSession` is already active.

    Returns:
      time: a human-readable time formatted string. Represents the time that the session ended.
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
  
  async def clear_queue(self) -> None:
    """
    Clears the queue.

    Sets `repeat` to False.

    Current song will play to completion, and will only stop if skipped or bot leaves.

    Raises:
      ClearQueueError: something went wrong when clearing the queue, or repeating. Caught with default `Exception` class, here for the case that clearing the queue or setting repeat = False fails.
    """
    try:
      # Clear queue
      self.queue.clear()
      self.loop = False

    except Exception:
      raise clear_queue_error.ClearQueueError(f"There was an error clearing the queue. Check logs for more details", "clear_queue", "somehow .clear() or .stop() failed")

  def q_to_embed(self) -> discord.Embed:
    """
    Transforms the current queue to an embed.
    Returns:
      Embed containing the queue:
      Format:
      ```
        1. SongTitle [SongDuration]
        ...
      ```
    """
    embed = discord.Embed(title="Now Playing: " if self.current else "Nothing playing.", description=f"**{self.current.title}** [{self.current.format_duration}]" if self.current else "")
    if self.queue:
      # Format the queue as:
      #   1. SongTitle 
      #   2. ...
      queue_str = "\n".join(f"`{i}`. {song.title} [{song.format_duration}]" for i, song in enumerate(self.queue, start=1))
      embed.add_field(name="Queue: ", value=queue_str, inline=False)

    # make it look nicer with the bottom 4 buttons
    embed.add_field(name="",value=f"Repeat: {'On' if self.loop else 'Off'}\n{len(self.queue)} songs in queue.")
    return embed
  
  async def cleanup_voice(self) -> None:
    """
    Cleans up the voice client.

    1. Clears the queue.
    2. Disconnects the bot from VC.
    3. Cleans up any existing views.

    Called whenever the queue is empty or /leave is called.
    """
    if self.voice_client:
      self.current = None
      await self.clear_queue()
      await self.voice_client.disconnect()
      await self.cleanup_view("Left the vc by command.")

  async def cleanup_view(self, reason: str = "*All songs have been played.") -> None:
    """
    Cleans up any existing views. May be called by expiration or disabling.

    Will send a message and then disables all buttons.
    """
    if self.active_view:
      await self.active_view.expire_cleanup(reason)
      self.active_view = None

  async def send(self, message: str) -> None:
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
