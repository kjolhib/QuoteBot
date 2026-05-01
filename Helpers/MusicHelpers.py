import yt_dlp
import asyncio
import discord
from typing import Any

from interaction_type import QuoteBotInteraction

from exceptions.voice import user_in_stage_vc_error, user_not_in_vc_error, no_voice_error
from exceptions.voice import after_play_error
from .UtilityHelpers import safe_send
from classes.guild_state import GuildState

async def play_next_song(interaction: QuoteBotInteraction, state: GuildState):
  """
  Plays the next song in queue.
 
  Repeat is handled automatically.
  
  Disconnects if queue is empty and repeat is off.

  Args:
    state: the GuildState class
  """
  if not state.voice_client:
    raise no_voice_error.NoVoiceClientError("Voice client not found while attempting to play the next song, @chewswisely messed something up. Check logs for more details.", "play_next_song", "when attempting to play the next song, guild's voice_client attribute suddenly became None. This can only happen if the bot disconnected.")

  ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -c:a libopus -b:a 96k",
  }
  def after_play(error: Any):
    """
    Schedules the next song
    """
    if error:
      # If any error occurs here, report it, but continue playing the queue
      raise after_play_error.AfterPlayError("An error occurred after song stopped. @chewswisely messed something up.", "after_play", "")
    # schedule next song
    if state.voice_client:
      asyncio.run_coroutine_threadsafe(
        play_next_song(interaction, state), state.voice_client.loop
      )
  
  if state.repeat and state.current:
    # Loop current song
    audio_url, title = state.current
    now_msg = f"Now repeating: **{title}**"
  elif state.queue:
    # no loop, pop next in queue and play
    audio_url, title = state.queue.popleft()
    state.current = (audio_url, title)
    now_msg = f"Now playing: **{title}**"
  else:
    # Nothing to play, disconnect
    await state.cleanup_voice()
    print("[PLAY]: Disconnecting from voice call since no songs.")
    return
  
  source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options) # type: ignore
  
  # play song
  state.voice_client.play(source, after=after_play)
  
  # notify channels asynchornously
  asyncio.create_task(safe_send(interaction, now_msg))

async def ensure_vc(interaction: QuoteBotInteraction, user: discord.Member, play_cmd: bool=False) -> discord.VoiceClient | int:
  """
  Ensures user is in VC, bot joins the vc if they are.
  Args:
    user: user that requested the bot to join vc
    play_cmd: If called by `play_cmd`, then we play a song, if not, just join
  """
  user_name = user.mention
  # user must be in vc
  if not user.voice or not user.voice.channel:
    print("[PLAY]: ensure_vc: user is not in a vc.")
    raise user_not_in_vc_error.UserNotInVcError()

  # Check connections
  user_channel = user.voice.channel
  if isinstance(user_channel, discord.StageChannel):
    print("[PLAY]: ensure_vc: user is in a stage channel vc.")
    raise user_in_stage_vc_error.UserInStageVcError()

  return await _bot_join_vc(interaction, user_channel, user_name, play_cmd) # type: ignore
  
async def search_first_track(query: str, ydl_options: dict[str, Any]) -> tuple[str, str] | None:
  """
  Searches the query and returns the first track's audio url and title.
  Returns:
    (audio_url, title) if found
    None if not found or error
  """
  serach_query = "ytsearch1: " + query
  results = await _search_ytdlp_async(serach_query, ydl_options)
  tracks = results.get("entries", [])
  if not tracks:
    return None
  
  first = tracks[0]
  return first["url"], first.get("title", "Untitled")

async def _bot_join_vc(interaction: QuoteBotInteraction, user_channel: discord.VoiceChannel, user_name: str, play_cmd: bool):
  """
  Checks if the bot is already in vc.
  
  If not, joins.
  
  If is, moves if in different vc.
  Args:
    user_channel: the channel the user is in
    user_name: user's name
    play_cmd: whether or not this was called by the `/play` command.
  """
  # Check if bot is already in a VC in this guild
  bot_vc = interaction.guild.voice_client # type: ignore
  if bot_vc:
    if bot_vc.channel != user_channel:
      # bot already in channel, move
      await bot_vc.move_to(user_channel) # type: ignore
      await safe_send(interaction, f"By the tyranny of {user_name}, I have been moved to {user_channel}.")
    elif not play_cmd:
      await safe_send(interaction, "I am already in this channel!")
    return bot_vc
  else:
    # not in channel. connect
    print(f"[PLAY]: ensure_vc: Not in channel, connecting to {user_channel}")
    bot_vc = await user_channel.connect(timeout=5)
    await safe_send(interaction, f"Heed my arrival in {user_channel}, worm.")
    return bot_vc

def _extract(query: str, ydl_opts: dict[str, Any]):
  """
  Extracts the youtube query information.
  """
  with yt_dlp.YoutubeDL(ydl_opts) as ydl: # type: ignore
    return ydl.extract_info(query, download=False)

async def _search_ytdlp_async(query: str, ydl_opts: dict[str, Any]):
  """
  Asynchronously runs the searcher for seamlessness.
  
  Searches for the query.
  """
  loop = asyncio.get_running_loop()
  return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))

