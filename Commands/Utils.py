import discord
from typing import Optional, Any
from random import randint

# Helper imports
from Helpers.MusicBotHelpers import search_first_track, play_next_song, clear_queue, ensure_vc
from Helpers.UtilityHelpers import bot_require_voice_client, safe_send
from ErrorHandler import (ClearQueueError,
                          JoinVcError,
                          DateFormatError,
                          TimeFormatError,
                          UserInStageVcError,
                          UserNotInVcError)
from ErrorHandler.ErrorHandler import report_error
from Classes import GuildState as gs
from Helpers.TimezoneHelpers import convert_time

# OPUS_PATH = "/opt/homebrew/Cellar/opus/1.6.1/lib/libopus.0.dylib"

async def run_d(interaction: discord.Interaction, die_num: int, addon: Optional[int]=0):
  """
  Rolls a dice.
  Given die_num faces, where (die_num == 4) || (die_num >= 6), roll a dice where addon is added to the result.
  Params:
    - die_num: the faces of the die. Must be either exactly 4, or any number >= 6
    - addon: optional. The number added onto the result. Defaulted to 0
  """
  if (die_num < 6 and die_num != 4):
    await safe_send(interaction, f"I do not know what a D{die_num} is. Choose a die that has either 4 or 6 or more faces ya bingus.")
    return
  
  if not addon:
    addon = 0

  # Roll a randint from 1 to die_num
  roll = randint(1, die_num)
  addon_print = addon

  # If addon is not null, calculate new result by roll + addon and print appropriately formatted message
  if addon and addon_print != 0:
    sign = "+" if addon_print > 0 else "-"
    if addon_print < 0:
      addon_print = -addon_print
    print_msg = f"You have rolled a {roll} {sign} {addon_print} = **{roll + addon}** on a D{die_num}"
    # print(f"sign: '{sign}', addon: {addon}, roll: {roll}")
  else:
    print_msg = f"You have rolled a **{roll}** on a D{die_num}"
  await safe_send(interaction, print_msg)

async def run_join(interaction: discord.Interaction):
  """
  Joins vc.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  try:
    vc = await _ensure_voice(interaction) # type: ignore

    # Store vc in state
    state.voice_client = vc
  except UserNotInVcError.UserNotInVcError:
    await safe_send(interaction, f"You are not in a vc. Join a vc first!")
  except UserInStageVcError.UserInStageVcError:
    await safe_send(interaction, f"Cannot join Stage VC/Channels.")
  except JoinVcError.JoinVcError as jve:
    await safe_send(interaction, f"Error joining vc. Check logs for more details.")
    report_error("run_join", jve, f"error: JoinVcError joining vc: {jve}")
  except Exception as e:
    await safe_send(interaction, f"Unknown error when joining VC. Check logs for more details.")
    report_error("run_join", e, f"attempted to join vc: {e}")

async def run_play(interaction: discord.Interaction, query: str):
  """
  Plays a song based on query.
  Uses ytdlp library to download.
  Params:
    - query: the query or a link. Note, currently non-standard youtube links do NOT return any search results. 
  """
  # TODO: Modify the query if it's a non-standard yt link to a standard yt link. Probs use regex or otherwise to match and replace standard yt link
  # TODO: allow spotify links to playlists/song (?)

  # get or create state
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)

  # ensure user is in vc, if not, joins
  try:
    vc = await _ensure_voice(interaction, play_cmd=True) # type: ignore

    # Store vc in state
    state.voice_client = vc
  except UserNotInVcError.UserNotInVcError:
    await safe_send(interaction, f"You are not in a vc. Join a vc first!")
    return
  except UserInStageVcError.UserInStageVcError:
    await safe_send(interaction, f"Cannot join Stage VC/Channels.")
    return
  except JoinVcError.JoinVcError as jve:
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
async def run_skip(interaction: discord.Interaction) -> None:
  """
  Skips the currently playing song.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  if not state or not state.voice_client or not state.voice_client.is_playing():
    return await safe_send(interaction, "No songs playing.")
  
  state.voice_client.stop() # triggers playnextsong
  await safe_send(interaction, "Skipping current song...")

@bot_require_voice_client
async def run_pause(interaction: discord.Interaction) -> None:
  """
  Pauses the playing song.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
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
async def run_resume(interaction: discord.Interaction):
  """
  Resumes the paused song.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
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
async def run_leave(interaction: discord.Interaction) -> None:
  """
  Leaves the VC.
  Clears the queue.
  """
  guild_id = str(interaction.guild_id)
  state: gs.GuildState = gs.get_guild_state(guild_id)

  try:
    await clear_queue(state)
    await state.voice_client.disconnect() # type: ignore
    await safe_send(interaction, "I hath vanished.")
  except ClearQueueError.ClearQueueError as cqe:
    await safe_send(interaction, f"Error clearing queue. Check logs for more details.")
    report_error("run_leave", cqe, f"error clearing queue: {cqe}")
  except Exception as e:
    await safe_send(interaction, f"Error leaving vc. Check logs for more details.")
    report_error("run_leave", e, f"error leaving vc: {e}")

@bot_require_voice_client
async def run_clear_queue(interaction: discord.Interaction) -> None:
  """
  Clears the queue of all songs.
  """
  guild_id = str(interaction.guild_id)
  state: gs.GuildState = gs.get_guild_state(guild_id)

  try:
    await clear_queue(state)
    await safe_send(interaction, "Queue cleared.")
  except ClearQueueError.ClearQueueError as cqe:
    await safe_send(interaction, f"Error clearing queue. Check logs for more details.")
    report_error("run_clear_queue", cqe, f"error clearing queue: {cqe}")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while clearing queue. Check logs for more details.")
    report_error("run_clear_queue", e, f"error clearing queue: {e}")

@bot_require_voice_client
async def run_repeat(interaction: discord.Interaction):
  """
  Loops the current song if not looping, if looping already, stop looping.
  Sets the guild state's repeat field to true.

  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  if not state or not state.current:
    return await safe_send(interaction, "No songs are playing.")
  
  # flip flop: loop <-> no loop
  state.repeat = not state.repeat
  msg = f"Looping current song: {state.current[1]}" if state.repeat else "Will now stop looping."
  await safe_send(interaction, msg)

@bot_require_voice_client
async def run_list_queue(interaction: discord.Interaction):
  """
  Lists the songs in queue.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  
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

async def run_timezone_converter(
  interaction: discord.Interaction,
  time: str,
  origin_country: str,
  origin_city: str, 
  target_country: str,
  target_city: str,
  date_str: str | None = None
):
  """
  Timezone converter
  """
  try:
    dt_origin, dt_target = convert_time(
      time,
      origin_country,
      origin_city,
      target_country,
      target_city,
      date_str
    )

    # No errors
    await safe_send(interaction,
f"""
**Time Conversion:**
Origin: {origin_city}, {origin_country} [{dt_origin}]
Target: {target_city}, {target_country} [{dt_target}]
"""
                          )
  except DateFormatError:
    await safe_send(interaction, "Date must be in the format DD/MM/YYYY")
    print(f"[TIMEZONE]: incorrect date format.")
  except TimeFormatError:
    await safe_send(interaction, "Time must be in the format HH:MM")
    print(f"[TIMEZONE]: incorrect time format.")
  except Exception as e:
    await safe_send(interaction, 
f"""
Failed to convert:
[{time}], {date_str}, {origin_city}, {origin_country} to {target_city}, {target_country}
"""
                      )
    report_error("run_timezone_converter", e, 
                 f"""error converting timezone: {e}:
origin_country: {origin_country},
origin_city: {origin_city},
target_country: {target_country},
target_city: {target_city},
origin_date: {date_str}
"""
                 )

"""
Helper functions
"""
async def _ensure_voice(interaction: discord.Interaction, play_cmd: bool=False) -> discord.VoiceClient:
  """
  Ensures the bot is in a vc, if not, joins the vc that the user is in.
  """
  vc = await ensure_vc(interaction, interaction.user, play_cmd=play_cmd) # type: ignore 
  if not isinstance(vc, discord.VoiceClient):
    raise JoinVcError.JoinVcError("Voice client returned an unknown error.")
  return vc
