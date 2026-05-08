import re
import yt_dlp
import asyncio
import discord
from typing import Any

from interaction_type import QuoteBotInteraction

from classes.song import Song
from exceptions.voice import user_in_stage_vc_error, user_not_in_vc_error, no_voice_error
from exceptions.voice import after_play_error
from .utility_helpers import safe_send
from classes.guild_state import GuildState

_YT_URL_PATTERNS = [
  r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})', # youtu.be link
  r'(?:https?://)?(?:www\.|m\.)?youtube\.com/watch\?.*?v=([a-zA-Z0-9_-]{11})', # https://www.youtube.com/watch
  r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})', # standard youtube shorts url
  r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})' # embed links
]

def normalise_yt_url(query: str) -> tuple[str, bool]:
  """
  Returns a normalised youtube url.

  If the query has any youtube variant, returns the standard "watch?v=`url`".

  If query is a plain query search (ie. plain english), returns it unchanged.

  Args:
    query: the string containing user's input, fed through the pattern matcher
  Returns:
    Format:
      `(norm_url, is_url)`
  """
  video_id = _extract_video_id(query)
  if video_id:
    return (f"https://www.youtube.com/watch?v={video_id}", True)
  return (query, False)


async def play_next_song(state: GuildState):
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
        play_next_song(state), state.voice_client.loop
      )
  
  # differentiate between repeating or not
  if state.loop and state.current:
    # Loop current song
    song = state.current
    now_msg = f"Now repeating: **{song.title}** [{song.format_duration}]"
  elif state.queue:
    # no loop, pop next in queue and play
    song = state.queue.popleft()
    state.current = song
    now_msg = f"Now playing: **{song.title}** [{song.format_duration}]"
  else:
    # Nothing to play, disconnect
    await state.cleanup_voice()
    print("[PLAY]: Disconnecting from voice call since no songs.")
    return
  
  source = discord.FFmpegOpusAudio(song.url, **ffmpeg_options) # type: ignore
  
  # play song
  state.voice_client.play(source, after=after_play)
  
  # notify channels asynchornously
  if state.text_channel:
    await state.send(now_msg)

  # Update the view.
  if state.active_view and state.active_view.message:
    await state.active_view.edit_view(embed=state.q_to_embed(), force_playing=True)

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
  
async def search_first_track(query: str, ydl_options: dict[str, Any]) -> Song | None:
  """
  Searches the query and returns the first track's audio url and title.
  Args:
    query: string containing the user's inputs
    ydl_options: hard coded options for ytdlp
  Returns:
    (audio_url, title): if found
    None: if not found or error
  """
  # Attempt to normalise a youtube url. Returns either a standard yt url if is url, or a string if not.
  normalised, is_url = normalise_yt_url(query)
  if is_url:
    # Direct url in the form https://www.youtube.com/watchv=<url>
    result = await _search_ytdlp_async(normalised, ydl_options)
    if not result or "url" not in result:
      return None
    return Song(
      title=result.get("title", "Untitled"), # type: ignore
      url=result["url"], # type: ignore
      song_length=result.get("duration", 0) # type: ignore
    )
  else:
    # Plain english search, wrap it with ytsearch1 and grab the first entry
    results = await _search_ytdlp_async(f"ytsearch1: {normalised}", ydl_options)
    tracks = results.get("entries", [])
    if not tracks:
      return None
    
    first = tracks[0]
    return Song(title=first.get("title", "Untitled"), url=first["url"], song_length=first.get("duration", 0))

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

def _extract_video_id(query: str) -> str | None:
  """
  Given a query, extract the matching pattern.
  Args:
    query: the string containing the user's input
  Returns:
    str: the matching pattern
    None: no matching found
  """
  for i, pattern in enumerate(_YT_URL_PATTERNS):
    match = re.search(pattern, query)
    if match:
      print(f"[EXTRACT_VIDEO_ID]: Normaliser: Matched pattern [{i}]: {pattern}")
      print(f"[EXTRACT_VIDEO_ID]: Extracted into normalised url: {match.group(1)}")
      return match.group(1)
  print(f"[EXTRACT_VIDEO_ID]: Normaliser: no pattern matches for query {query}")
  return None
