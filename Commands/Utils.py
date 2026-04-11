import discord
from typing import Optional, Any
from Helpers.MusicBot_helpers import search_ytdlp_async, play_next_song, clear_queue, ensure_vc
from Helpers.Utility_helpers import safe_send
from random import randint
from ErrorHandler import ErrorHandler as eh
from Classes import GuildState as gs
from Helpers.Timezone_helper import convert_time

OPUS_PATH = "/opt/homebrew/Cellar/opus/1.6.1/lib/libopus.0.dylib"

async def run_d(interaction: discord.Interaction, die_num: int, addon: Optional[int]=0):
  """
  Rolls a dice.
  Given die_num faces, where die_num == (4 || >= 6), roll a dice where addon is added to the result.
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
  Error codes:
    - 401: User is currently not in vc
    - 402: User is in a "stage vc". Bots cannot join stage vcs
    - 403: Error attempting to join vc. The checks above passed
  """
  try:
    guild_id = str(interaction.guild_id)
    state = gs.get_guild_state(guild_id)
    
    user = interaction.user
    vc = await ensure_vc(interaction, user) # type: ignore
    if not vc:
      # error
      await safe_send(interaction, f"Error joining vc.")
      return
    elif vc == 401:
      # not invc
      await safe_send(interaction, f"User {user} is not in a vc.")
      return
    elif vc == 402:
      # user is in stage vc
      await safe_send(interaction, "Cannot join Stage Channels.")
      return
    elif vc == 403:
      # an error when trying to join
      await safe_send(interaction, "Error joining vc.")
      return

    # Store vc in state
    if isinstance(vc, discord.VoiceClient):
      state.voice_client = vc
    else:
      print(f"[ERROR]: run_join: fatal error: uncaught int return type from ensure_vc")
      await safe_send(interaction, "Voice client returned an unknown error. Check logs for more info.")
  except Exception as e:
    await interaction.response.send_message(f"Fatal: exception joining vc: {e}")
    err = eh.Error(e, "/join")
    eh.report_error(err)

async def run_play(interaction: discord.Interaction, query: str):
  """
  Plays a song based on query.
  Uses ytdlp library to download.
  Params:
    - query: the query or a link. Note, currently non-standard youtube links do NOT return any search results. 
  """
  # TODO: Modify the query if it's a non-standard yt link to a standard yt link. Probs use regex or otherwise to match and replace standard yt link

  # get or create state
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  user = interaction.user

  # ensure user is in vc, if not, joins
  vc = await ensure_vc(interaction, user, play_cmd=True) # type: ignore
  if not vc:
    # error
    await safe_send(interaction, f"Error joining vc.")
    return
  elif vc == 401:
    # not invc
    await safe_send(interaction, f"User {user} is not in a vc.")
    return
  elif vc == 402:
    # user is in stage vc
    await safe_send(interaction, "Cannot join Stage Channels.")
    return
  elif vc == 403:
    await safe_send(interaction, "Error joining vc.")
    return

  if isinstance(vc, discord.VoiceClient):
      state.voice_client = vc
  else:
    print(f"[ERROR]: run_join: fatal error: uncaught int return type from ensure_vc")
    await safe_send(interaction, "Voice client returned an unknown error. Check logs for more info.")

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
  search_query = "ytsearch1: " + query
  results = await search_ytdlp_async(search_query, ydl_options)

  # Get the tracks
  tracks = results.get("entries", []) # type: ignore

  # No tracks found
  if tracks is None:
    await safe_send(interaction, "No results found.")
    return
  
  # Extract tracks
  if tracks:
    first_track = tracks[0]
  else:
    await safe_send(interaction, f"No results found.")
    return
  # print(first_track)

  # Get the first track
  print(f"[PLAY] Found track: {first_track['title']}")
  audio_url = first_track["url"]
  title = first_track.get("title", "Untitled")

  # append song to queue
  state.queue.append((audio_url, title))

  # if currently playing or paused, send notifiaction that the song is added to queue.
  if not isinstance(vc, int) and (vc.is_playing() or vc.is_paused()):
    await safe_send(interaction, f"Added to queue: **{title}**.")
  else:
    # otherwise, play the song now.
    await play_next_song(state, interaction)
  
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

async def run_pause(interaction: discord.Interaction) -> None:
  """
  Pauses the playing song.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  vc: discord.VoiceClient | None = state.voice_client

  # If bot is in vc
  if not vc:
    return await safe_send(interaction, "I am not in a voice channel, invite me now.")
  
  # If not playing
  if not vc.is_playing():
    return await safe_send(interaction, "No songs are playing ya bingus.")
  
  try:
    # Pause the track
    vc.pause()
    await safe_send(interaction, "Song has been paused.")
  except Exception as e:
    print(f"[ERROR]: run_pause: {e}")
    await safe_send(interaction, f"Error pausing... check logs.")
    err = eh.Error(e, "/pause")
    eh.report_error(err)

async def run_resume(interaction: discord.Interaction):
  """
  Resumes the paused song.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)

  # If bot is in vc
  if state.voice_client is None:
    return await safe_send(interaction, "I am not in a voice channel, invite me please.")
  
  # If not pause
  if not state.voice_client.is_paused():
    return await safe_send(interaction, "No songs are paused right now yo bunga.")
  
  try:
    # Resume the track
    state.voice_client.resume()
    await safe_send(interaction, "Resuming...")
  except Exception as e:
    await safe_send(interaction, "Error resuming... check logs.")
    print(f"[ERROR]: resume: {e}")
    err = eh.Error(e, "/resume")
    eh.report_error(err)

async def run_leave(interaction: discord.Interaction) -> None:
  """
  Leaves the VC.
  Clears the queue.
  """
  guild_id = str(interaction.guild_id)
  state: gs.GuildState = gs.get_guild_state(guild_id)

  # not in vc or connected
  if not state or not state.voice_client or not state.voice_client.is_connected():
    return await safe_send(interaction, "Not in vc.")
  await clear_queue(interaction, state)

  try:
    await state.voice_client.disconnect()
    await safe_send(interaction, "I hath vanished.")
  except Exception as e:
    await safe_send(interaction, f"[ERROR]: stop: {e}")
    err = eh.Error(e, "/stop")
    eh.report_error(err)

async def run_repeat(interaction: discord.Interaction):
  """
  Loops the current song if not looping, if looping already, stop looping. Flip flop
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

async def run_list_queue(interaction: discord.Interaction):
  """
  Lists the songs in queue.
  """
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  if not state or not state.voice_client or not state.voice_client.is_connected():
    # not state, not in a vc or not connected
    await safe_send(interaction, "I am not in a voice channel.")
    return
  
  # empty queue
  if not state.queue and not state.current:
    await interaction.followup.send("Queue is empty.")
    return
  
  # Current title and the queue formatting
  cur_title = state.current[1] if state.current else "Nothing Playing"
  result = f"Currently playing: **{cur_title}** \n**Current Queue:**\n"
  for idx, (_, title) in enumerate(state.queue, start=1):
    result += f"{idx}. {title}\n"
  
  await interaction.followup.send(result)

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
      target_city
    )

    # Error codes
    if dt_origin == 401:
      await safe_send(interaction, dt_target) # type: ignore
      return
    elif dt_origin == 402:
      await safe_send(interaction, dt_target) # type: ignore
      return
    elif dt_origin == 400 and dt_target == 400:
      await safe_send(interaction, dt_target) # type: ignore
      return
    elif dt_origin == 403 and dt_target == 403:
      await safe_send(interaction, 
f"""
Failed to convert:
[{time}], {date_str}, {origin_city}, {origin_country} to {target_city}, {target_country}
"""
                      )
      return

    # No errors
    await safe_send(interaction,
f"""
**Time Conversion:**
Origin: {origin_city}, {origin_country} [{dt_origin}]
Target: {target_city}, {target_country} [{dt_target}]
"""
                          )
  except Exception as e:
    err = eh.Error(str(e), "run_timezone_converter")
    eh.report_error(err)
    await safe_send(interaction, f"Time zone converter failed: {e}")
