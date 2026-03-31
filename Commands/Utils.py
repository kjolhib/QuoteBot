import discord
from Helpers.MusicBot_helpers import search_ytdlp_async, play_next_song, clear_queue, ensure_vc
from Helpers.Utility_helpers import safe_send
from collections import deque
from random import randint
from ErrorHandler import ErrorHandler as eh
from Classes import GuildState as gs
from Helpers.Timezone_helper import convert_time

OPUS_PATH = "/opt/homebrew/Cellar/opus/1.6.1/lib/libopus.0.dylib"

"""
Command Runners
"""
async def run_d(interaction, die_num, addon=0):
  if (die_num < 6 and die_num != 4):
    await safe_send(interaction, f"I do not know what a D{die_num} is. Choose a die that has either 4 or 6 or more faces ya bingus.")
    return
  roll = randint(1, die_num)
  addon_print = addon
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
  try:
    guild_id = str(interaction.guild_id)
    state = gs.get_guild_state(guild_id)
    
    user = interaction.user
    vc = await ensure_vc(interaction, user)
    if vc is None:
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

    # Store vc in state
    state.voice_client = vc
  except Exception as e:
    await interaction.response.send_message(f"Fatal: exception joining vc: {e}")
    err = eh.Error(e, "/join")
    eh.report_error(err)

async def run_play(interaction: discord.Interaction, query: str):
  guild_id = str(interaction.guild_id)

  # get or create state
  state = gs.get_guild_state(guild_id)

  user = interaction.user
  voice_client = await ensure_vc(interaction, user, play_cmd=True)
  if voice_client is None:
    # error
    await safe_send(interaction, f"Error joining vc.")
    return
  elif voice_client == 401:
    # not invc
    await safe_send(interaction, f"User {user} is not in a vc.")
    return
  elif voice_client == 402:
    # user is in stage vc
    await safe_send(interaction, "Cannot join Stage Channels.")
    return
  elif voice_client == 403:
    await safe_send(interaction, "Error joining vc.")
    return

  state.voice_client = voice_client

  # Search
  ydl_options = {
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
  results = await search_ytdlp_async(search_query, ydl_options, {guild_id: state.queue})

  # Get the tracks
  tracks = results.get("entries", [])

  # No tracks found
  if tracks is None:
    await interaction.followup.send("No results found.")
    return
  
  # Extract tracks
  if tracks:
    first_track = tracks[0]
  else:
    await interaction.followup.send(f"No results found.")
    return
  # print(first_track)
  print(f"[PLAY] Found track: {first_track['title']}")
  audio_url = first_track["url"]
  title = first_track.get("title", "Untitled")

  state.queue.append((audio_url, title))
  # Is playing or not, appends to queue or not
  if voice_client.is_playing() or voice_client.is_paused():
    await interaction.followup.send(f"Added to queue: **{title}**.")
  else:
    # await interaction.followup.send(f"Now playing: **{title}**.")
    await play_next_song(state, interaction)
  
async def run_skip(interaction):
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  if not state or not state.voice_client or not state.voice_client.is_playing():
    return await safe_send(interaction, "No songs playing.")
  
  state.voice_client.stop() # triggers playnextsong
  await safe_send(interaction, "Skipping current song...")

async def run_pause(interaction):
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)

  # If bot is in vc
  if state.voice_client is None:
    return await safe_send(interaction, "I am not in a voice channel, invite me now.")
  
  # If not playing
  if not state.voice_client.is_playing():
    return await safe_send(interaction, "No songs are playing ya bingus.")
  
  try:
    # Pause the track
    state.voice_client.pause()
    await safe_send(interaction, "Song has been paused.")
  except Exception as e:
    print(f"[ERROR]: run_pause: {e}")
    await safe_send(interaction, f"Error pausing... check logs.")
    err = eh.Error(e, "/pause")
    eh.report_error(err)

async def run_resume(interaction):
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

async def run_leave(interaction):
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)

  # not in vc or connected
  if not state or not state.voice_client.is_connected():
    return await safe_send(interaction, "Not in vc.")
  await clear_queue(interaction, state)

  try:
    await state.voice_client.disconnect()
    await safe_send(interaction, "I hath vanished.")
  except Exception as e:
    await safe_send(interaction, f"[ERROR]: stop: {e}")
    err = eh.Error(e, "/stop")
    eh.report_error(err)

async def run_repeat(interaction):
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  if not state or not state.current:
    return await safe_send(interaction, "No songs are playing.")
  
  # flip flop
  state.repeat = not state.repeat
  msg = f"Looping current song: {state.current[1]}" if state.repeat else "Will now stop looping."
  await safe_send(interaction, msg)

async def run_list_queue(interaction: discord.Interaction):
  guild_id = str(interaction.guild_id)
  state = gs.get_guild_state(guild_id)
  if not state or not state.voice_client or not state.voice_client.is_connected():
    # not state, not in a vc or not connected
    await safe_send(interaction, "I am not in a voice channel.")
    return
  
  # empty queue
  if state.queue is None and not state.current:
    await interaction.followup.send("Queue is empty.")
    return
  
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
      await safe_send(interaction, dt_target)
      return
    elif dt_origin == 402:
      await safe_send(interaction, dt_target)
      return
    elif dt_origin == 400 and dt_target == 400:
      await safe_send(interaction, dt_target)
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
