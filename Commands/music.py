import discord
from typing import Any

from interaction_type import QuoteBotInteraction
from classes.music_interaction import MusicPlayer
from helpers.MusicHelpers import search_first_track, play_next_song, ensure_vc
from helpers.UtilityHelpers import bot_require_voice_client, safe_send
from exceptions.voice import join_vc_error

async def run_join(interaction: QuoteBotInteraction):
  """
  Joins vc.
  Raises:
    UserNotInVcError: user who invoked this command is not in vc
    UserInStageVcError: user who invoked this command is in a stage vc
    JoinVcError: an unknown error occurred when attempting to join vc. Uncaught error.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  vc = await _ensure_voice(interaction) # type: ignore

  # Store vc in state
  state.voice_client = vc

async def run_play(interaction: QuoteBotInteraction, query: str):
  """
  Plays a song based on query.
  
  Uses ytdlp library to download.
  Args:
    query: the query or a link. 
    
  Raises:
    UserNotInVcError: user who invoked this command is not in vc
    UserInStageVcError: user who invoked this command is in a stage vc
    JoinVcError: an unknown error occurred when attempting to join vc. Uncaught error.

  Note, currently non-standard youtube links do NOT return any search results. 
  """
  # TODO: Modify the query if it's a non-standard yt link to a standard yt link. Probs use regex or otherwise to match and replace standard yt link
  # TODO: allow spotify links to playlists/song (?)

  # get or create state
  state = interaction.client.get_guild_state(str(interaction.guild_id))

  # ensure user is in vc, if not, joins
  vc = await _ensure_voice(interaction, play_cmd=True) # type: ignore

  # Store vc in state
  state.voice_client = vc
  
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
  song = await search_first_track(query, ydl_options)
  if not song:
    await safe_send(interaction, f"No results found.")
    return

  # Queue or play
  print(f"[PLAY] Found track: {song.title}")
  state.queue.append(song)

  # if currently playing or paused, send notifiaction that the song is added to queue.
  if vc.is_playing() or vc.is_paused():
    await safe_send(interaction, f"Added to queue: **{song.title}** [{song.format_duration}].")
  else:
    # otherwise, play the song now.
    await play_next_song(interaction, state)
  
@bot_require_voice_client
async def run_skip(interaction: QuoteBotInteraction) -> None:
  """
  Skips the currently playing song.
  
  Requires the bot to be in a VC.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  if not state or not state.voice_client or not state.voice_client.is_playing():
    await safe_send(interaction, "No songs playing.")
    return
  
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
    await safe_send(interaction, "No songs are playing ya bingus.")
    return
  
  # Pause the track
  vc.pause()
  await safe_send(interaction, "Song has been paused.")

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
  
  # Resume the track
  state.voice_client.resume() # type: ignore
  await safe_send(interaction, "Resuming...")

@bot_require_voice_client
async def run_leave(interaction: QuoteBotInteraction) -> None:
  """
  Leaves the VC.

  Clears the queue.

  Raises:
    ClearQueueError: something happened while attempting to clear the queue. Uncaught error
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))

  await state.cleanup_voice()
  await safe_send(interaction, "I hath vanished.")

@bot_require_voice_client
async def run_clear_queue(interaction: QuoteBotInteraction) -> None:
  """
  Clears the queue of all songs.

  Raises:
    ClearQueueError: uncaught error attempting to clear music queue.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))

  await state.clear_queue()
  await safe_send(interaction, "Queue cleared.")

@bot_require_voice_client
async def run_repeat(interaction: QuoteBotInteraction):
  """
  Loops the current song if not looping, if looping already, stop looping.
  
  Sets the guild state's `repeat` field to true.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  if not state or not state.current:
    return await safe_send(interaction, "No songs are playing.")
  
  # flip flop: loop <-> no loop
  state.repeat = not state.repeat
  msg = f"Looping current song: **{state.current.title}** [{state.current.format_duration}]" if state.repeat else "Will now stop looping."
  await safe_send(interaction, msg)

@bot_require_voice_client
async def run_list_queue(interaction: QuoteBotInteraction):
  """
  Lists the songs in queue.

  Returns:
    A string containing information about the queue.
    Format:
      Currently playing {song}
      Current Queue:
        ...
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  
  # empty queue
  if not state.queue and not state.current:
    await safe_send(interaction, "Queue is empty.")
    return
  
  await state.cleanup_view("*Another MusicPlayer has been created.")

  # Current title and the queue formatting
  embed = state.q_to_embed()
  view = MusicPlayer(state)
  msg = await safe_send(interaction, embeds=embed, view=view)
  view.message = msg
  state.active_view = view

"""
Helper functions
"""
async def _ensure_voice(interaction: QuoteBotInteraction, play_cmd: bool=False) -> discord.VoiceClient:
  """
  Ensures the bot is in a vc, if not, joins the vc that the user is in.
  """
  vc = await ensure_vc(interaction, interaction.user, play_cmd=play_cmd) # type: ignore 
  if not isinstance(vc, discord.VoiceClient):
    raise join_vc_error.JoinVcError("An error occurred when attempting to join vc.", "_ensure_voice", "ensure_vc helper did not join vc. It should have checked whether or not client is in vc, if not, join it.")
  return vc

