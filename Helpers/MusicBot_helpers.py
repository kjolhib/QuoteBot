import yt_dlp
import asyncio
import discord
from ErrorHandler import ErrorHandler as eh
from .Utility_helpers import safe_send
from Classes.GuildState import GuildState

# Helpers for the music bot features in QuoteBot
async def search_ytdlp_async(query, ydl_opts):
  """
  Asynchronously runs the searcher for seamlessness.
  Searches for the query.
  """
  try:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))
  except Exception as e:
    err = eh.Error(e, "/play/search_ytdlp_async")
    eh.report_error(err)

# Helper for search_ytdlp_async
def _extract(query, ydl_opts):
  """
  Extracts the youtube query information
  """
  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      return ydl.extract_info(query, download=False)
  except Exception as e:
    err = eh.Error(e, "/play/_extract")
    eh.report_error(err)
  
async def play_next_song(state: GuildState, interaction: discord.Interaction):
  """
  Plays the next song in queue.
  Repeat is handled automatically.
  Disconnects if queue is empty and repeat is off.
  """
  if not state.voice_client:
    return

  ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -c:a libopus -b:a 96k",
  }
  def after_play(error):
    """
    Schedules the next song
    """
    if error:
      print(f"[ERROR] playing {title}: {error}")
      err = eh.Error(error, "/play: play_next_song")
      eh.report_error(err)
    # schedule next song
    asyncio.run_coroutine_threadsafe(
      play_next_song(state, interaction), state.voice_client.loop
    )
  
  if state.repeat and state.current:
    # Loop current song
    audio_url, title = state.current
    now_msg = f"Now repeating: **{title}**"
  elif state.queue:
    audio_url, title = state.queue.popleft()
    state.current = (audio_url, title)
    now_msg = f"Now playing: **{title}**"
  else:
    # Nothing to play, disconnect
    await state.voice_client.disconnect()
    print("Disconnecting from voice call since no songs.")
    state.current = None
    return
  
  source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options)
  
  # play song
  state.voice_client.play(source, after=after_play)
  
  # notify channels asynchornously
  asyncio.create_task(safe_send(interaction, now_msg))

async def clear_queue(interaction: discord.Interaction, state: GuildState):
  """
  Clears the queue
  """
  try:
    # Clear queue
    state.queue.clear()
    state.current = None
    state.repeat = False

    if state.voice_client.is_playing() or state.voice_client.is_paused():
      state.voice_client.stop()
  except Exception as e:
    err = eh.Error(e, "/stop/clear_queue")
    eh.report_error(err)

# Check if bot is in vc, if not join,
async def bot_join_vc(interaction, user_channel, user_name, play_cmd):
  """
  Checks if the bot is already in vc.
  If not, joins.
  If is, moves if in different vc.
  Params:
    - user_channel: the channel the user is in
    - user_name: user's name
    - play_cmd: whether or not this was called by the /play command.
  """
  # Check if bot is already in a VC in this guild
  bot_vc = interaction.guild.voice_client
  try:
    if bot_vc:
      if bot_vc.channel != user_channel:
        # bot already in channel, move
        await bot_vc.move_to(user_channel)
        await safe_send(interaction, f"By the tyranny of {user_name}, I have been moved to {user_channel}.")
      elif not play_cmd:
        await safe_send(interaction, "I am already in this channel!")
      return bot_vc
    else:
      # not in channel. connect
      print(f"[PLAY]: ensure_vc: Not in channel, connecting to {user_channel}")
      bot_vc = await user_channel.connect(timeout=30)
      await safe_send(interaction, f"Heed my arrival in {user_channel}, worm.")
      return bot_vc
  except Exception as e:
    await safe_send(interaction, f"Fatal: error: /join: failed to join vc: {e}")
    err = eh.Error(e, "/play/ensure_vc")
    eh.report_error(err)
    return None

# Ensures that the bot is in vc
async def ensure_vc(interaction, user, play_cmd=False) -> discord.VoiceClient:
  """
  Ensures user is in VC, bot joins the vc if they are.
  Params:
    - user: user that requested the bot to join vc
    - play_cmd: If called by play_cmd, then we play a song, if not, just join
  Returns:
    - 401: User is not in VC
    - 402: User is in a stage vc
    - 403: An error joining vc. Above checks passed.
  """
  user_name = user.mention
  # user must be in vc
  if not user.voice or not user.voice.channel:
    print("[PLAY]: ensure_vc: user is not in a vc.")
    return 401

  user_channel = user.voice.channel
  # Check connections
  if isinstance(user_channel, discord.StageChannel):
    print("[PLAY]: ensure_vc: user is in a stage channel vc.")
    return 402

  try:
    return await bot_join_vc(interaction, user_channel, user_name, play_cmd)
  except Exception as e:
    print(f"[PLAY]: error joining vc: {e}")
    return 403
  