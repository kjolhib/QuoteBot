import discord
from typing import Any

from interaction_type import QuoteBotInteraction

from exceptions.music import clear_queue_error, join_vc_error, user_in_stage_vc_error
from helpers.MusicHelpers import search_first_track, play_next_song, clear_queue, ensure_vc
from helpers.UtilityHelpers import bot_require_voice_client, safe_send
from exceptions.music import (user_not_in_vc_error)
from exceptions.error_handler import report_error

async def run_join(interaction: QuoteBotInteraction):
  """
  Joins vc.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  try:
    vc = await _ensure_voice(interaction) # type: ignore

    # Store vc in state
    state.voice_client = vc
  except user_not_in_vc_error.UserNotInVcError:
    await safe_send(interaction, f"You are not in a vc. Join a vc first!")
  except user_in_stage_vc_error.UserInStageVcError:
    await safe_send(interaction, f"Cannot join Stage VC/Channels.")
  except join_vc_error.JoinVcError as jve:
    await safe_send(interaction, f"Error joining vc. Check logs for more details.")
    report_error("run_join", jve, f"error: JoinVcError joining vc: {jve}")
  except Exception as e:
    await safe_send(interaction, f"Unknown error when joining VC. Check logs for more details.")
    report_error("run_join", e, f"attempted to join vc: {e}")

async def run_play(interaction: QuoteBotInteraction, query: str):
  """
  Plays a song based on query.
  Uses ytdlp library to download.
  Params:
    - query: the query or a link. Note, currently non-standard youtube links do NOT return any search results. 
  """
  # TODO: Modify the query if it's a non-standard yt link to a standard yt link. Probs use regex or otherwise to match and replace standard yt link
  # TODO: allow spotify links to playlists/song (?)

  # get or create state
  state = interaction.client.get_guild_state(str(interaction.guild_id))

  # ensure user is in vc, if not, joins
  try:
    vc = await _ensure_voice(interaction, play_cmd=True) # type: ignore

    # Store vc in state
    state.voice_client = vc
  except user_not_in_vc_error.UserNotInVcError:
    await safe_send(interaction, f"You are not in a vc. Join a vc first!")
    return
  except user_in_stage_vc_error.UserInStageVcError:
    await safe_send(interaction, f"Cannot join Stage VC/Channels.")
    return
  except join_vc_error.JoinVcError as jve:
    await safe_send(interaction, f"Error joining vc. Check logs for more details.")
    report_error("run_play", jve, f"error: JoinVcError joining vc: {jve}")
    return
  except Exception as e:
    await safe_send(interaction, f"Unknown error when joining VC. Check logs for more details.")
    report_error("run_join", e, f"attempted to join vc: {e}")
    return
  
  # Search
  ydl_options: dict[str, Any] = {
    "format": "bestaudio[abr<=96]/bestaudio",
    "noplaylist": True,
    "youtube_include_dash_manifest": False,
    "youtube_include_hls_manifest": False,
    "js_runtimes": {
      "node": {}
    },
    "remote_components": ["ejs:github", "ejs:npm"]
  }
  track = await search_first_track(query, ydl_options)
  if not track:
    await safe_send(interaction, f"No results found.")
    return

  # Queue or play
  audio_url, title = track
  print(f"[PLAY] Found track: {title}")
  state.queue.append((audio_url, title))

  # if currently playing or paused, send notifiaction that the song is added to queue.
  if vc.is_playing() or vc.is_paused():
    await safe_send(interaction, f"Added to queue: **{title}**.")
  else:
    # otherwise, play the song now.
    try:
      await play_next_song(state, interaction)
    except Exception as e:
      await safe_send(interaction, f"Error playing song. Check logs for more details.")
      report_error("run_play", e, f"error playing song")
  
@bot_require_voice_client
async def run_skip(interaction: QuoteBotInteraction) -> None:
  """
  Skips the currently playing song.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  if not state or not state.voice_client or not state.voice_client.is_playing():
    return await safe_send(interaction, "No songs playing.")
  
  state.voice_client.stop() # triggers playnextsong
  await safe_send(interaction, "Skipping current song...")

@bot_require_voice_client
async def run_pause(interaction: QuoteBotInteraction) -> None:
  """
  Pauses the playing song.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  vc: discord.VoiceClient = state.voice_client # type: ignore

  # If not playing
  if not vc.is_playing():
    return await safe_send(interaction, "No songs are playing ya bingus.")
  
  try:
    # Pause the track
    vc.pause()
    await safe_send(interaction, "Song has been paused.")
  except Exception as e:
    await safe_send(interaction, f"Error pausing... Check logs for more details.")
    report_error("run_pause", e, f"error pausing song: {e}")

@bot_require_voice_client
async def run_resume(interaction: QuoteBotInteraction):
  """
  Resumes the paused song.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  vc = state.voice_client

  # If not pause
  if vc and not vc.is_paused():
    return await safe_send(interaction, "No songs are paused right now yo bunga.")
  
  try:
    # Resume the track
    state.voice_client.resume() # type: ignore
    await safe_send(interaction, "Resuming...")
  except Exception as e:
    await safe_send(interaction, "Error resuming... Check logs for more details.")
    report_error("run_resume", e, f"error resuming song: {e}")

@bot_require_voice_client
async def run_leave(interaction: QuoteBotInteraction) -> None:
  """
  Leaves the VC.
  Clears the queue.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))

  try:
    await clear_queue(state)
    await state.voice_client.disconnect() # type: ignore
    await safe_send(interaction, "I hath vanished.")
  except clear_queue_error.ClearQueueError as cqe:
    await safe_send(interaction, f"Error clearing queue. Check logs for more details.")
    report_error("run_leave", cqe, f"error clearing queue: {cqe}")
  except Exception as e:
    await safe_send(interaction, f"Error leaving vc. Check logs for more details.")
    report_error("run_leave", e, f"error leaving vc: {e}")

@bot_require_voice_client
async def run_clear_queue(interaction: QuoteBotInteraction) -> None:
  """
  Clears the queue of all songs.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))

  try:
    await clear_queue(state)
    await safe_send(interaction, "Queue cleared.")
  except clear_queue_error.ClearQueueError as cqe:
    await safe_send(interaction, f"Error clearing queue. Check logs for more details.")
    report_error("run_clear_queue", cqe, f"error clearing queue: {cqe}")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while clearing queue. Check logs for more details.")
    report_error("run_clear_queue", e, f"error clearing queue: {e}")

@bot_require_voice_client
async def run_repeat(interaction: QuoteBotInteraction):
  """
  Loops the current song if not looping, if looping already, stop looping.
  Sets the guild state's repeat field to true.

  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  if not state or not state.current:
    return await safe_send(interaction, "No songs are playing.")
  
  # flip flop: loop <-> no loop
  state.repeat = not state.repeat
  msg = f"Looping current song: {state.current[1]}" if state.repeat else "Will now stop looping."
  await safe_send(interaction, msg)

@bot_require_voice_client
async def run_list_queue(interaction: QuoteBotInteraction):
  """
  Lists the songs in queue.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  
  # empty queue
  if not state.queue and not state.current:
    await interaction.followup.send("Queue is empty.")
    return
  
  # Current title and the queue formatting
  cur_title = state.current[1] if state.current else "Nothing Playing"
  result = f"Currently playing: **{cur_title}** \n**Current Queue:**\n"
  for idx, (_, title) in enumerate(state.queue, start=1):
    result += f"{idx}. {title}\n"
  
  await safe_send(interaction, result)


"""
Helper functions
"""
async def _ensure_voice(interaction: QuoteBotInteraction, play_cmd: bool=False) -> discord.VoiceClient:
  """
  Ensures the bot is in a vc, if not, joins the vc that the user is in.
  """
  vc = await ensure_vc(interaction, interaction.user, play_cmd=play_cmd) # type: ignore 
  if not isinstance(vc, discord.VoiceClient):
    raise join_vc_error.JoinVcError("Voice client returned an unknown error.")
  return vc

