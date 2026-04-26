import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from typing import Optional

from interaction_type import QuoteBotInteraction

# Helper Imports
from classes.quote_bot import QuoteBot
from commands import utils, dnd, quotes, music
from helpers.UtilityHelpers import with_timeout
from exceptions.error_handler import configure_logging, report_error

# Init error logging
configure_logging()

# Load env data
load_dotenv()
def get_env(key: str) -> int:
  """
  Returns:
    integer of an env string
  """
  val = os.getenv(key)
  if val is None:
    raise ValueError(f"QuoteBot: Environment Initialisation error: {key} not found/set.")
  return int(val)

# Load tokens
BOT_TOKEN = os.getenv("QBOT_TOKEN")
if not BOT_TOKEN:
  raise ValueError("QuoteBot: Environment Initialisation error: bot_token not found/set.")
GUILD_IDS_PRIVATE = [
  get_env("DEV_SERVER"),
  get_env("GHIONCK")
]

client = QuoteBot()

@client.event
async def on_ready():
  print(f'QuoteBot: {client.user} started!')
  await client.tree.sync()

  # private commands
  for guild_id in GUILD_IDS_PRIVATE:
    guild = discord.Object(id=guild_id)
    try:
      # Give global access to most commands
      # Note. Some commands are specifically tailored for private use.
      # For the most part, this is because of the .json data I have stored on my local computer.
      # Don't want it messed up by other people from different servers.
      synced = await client.tree.sync(guild=guild)
      print(f"[SYNC] Synced {len(synced)} commands to guild {guild_id}")
    except Exception as e:
      report_error(f"error syncing commands to guild {guild_id}", e)
      print(f"[ERROR] syncing commands to guild {guild_id}: {e}")
    # await channel.send("QuoteBot is now online.")

# TODO: implement a loop that checks session active timer

@client.tree.command(name="start", description="Starts a dnd session")
@with_timeout(timeout=1)
async def start(interaction: QuoteBotInteraction):
  """
  Start a dnd session.

  Initialises dnd_session class.

  Sets `is_active` to be true.
  """
  await dnd.run_start(interaction)

@client.tree.command(name="end", description="End a dnd session")
@with_timeout(timeout=1)
async def end(interaction: QuoteBotInteraction):
  """
  Ends a dnd session.

  Sets `is_active` to be False.
  """
  await dnd.run_end(interaction)

@client.tree.command(name="new_die", description="Creates a new die instance with a scenario, with its own weights (dnd shi)")
@app_commands.describe(scenario="What do you want to use this die for?")
@app_commands.describe(faces="The number of faces this die has")
@with_timeout(timeout=3)
async def new_die(interaction: QuoteBotInteraction, scenario: str, faces: int):
  """
  Creates a new die instance named scenario with die_num number of faces.
  Args:
    scenario: the scenario the die would be used in, is weighted.
    die_num: the number of faces this die has. num != 4 and num > 5.
  """
  await dnd.run_new_die(interaction, scenario, faces)

@client.tree.command(name="remove_die", description="Deletes an instace die from this session")
@app_commands.describe(scenario="What is the scenario name of the die you want to remove?")
@with_timeout(timeout=3)
async def remove_die(interaction: QuoteBotInteraction, scenario: str):
  """
  Creates a new die instance named scenario with die_num number of faces.
  Args:
    scenario: the scenario the die would be used in, is weighted.
    die_num: the number of faces this die has. num != 4 and num > 5.
  """
  await dnd.run_remove_die_instance(interaction, scenario)

@client.tree.command(name="instance_die", description="Roll an existing scenario die")
@app_commands.describe(scenario="The die you want to roll")
@app_commands.describe(addon="Adds or subtracts this result from the die result")
@with_timeout(timeout=2)
async def instance_die(interaction: QuoteBotInteraction, scenario: str, addon: Optional[int]):
  """
  Takes a scnenario, and rolls the corresponding scenario's die.
  Args:
    scenario: the scenario that dictates the die.
  """
  await dnd.run_instance_die(interaction, scenario, addon)

@client.tree.command(name="list_dice", description="Lists all the instances of dice")
@with_timeout(timeout=2)
async def list_dice(interaction: QuoteBotInteraction):
  """
  Lists all the dice created in this session.
  Returns:
    A list of all dice created.
  """
  await dnd.run_list_die(interaction)

@client.tree.command(name="weather", description="Generate a random weather")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=1)
async def generate_weather(interaction: QuoteBotInteraction):
  """
  Generates a random weather using weighted chances.
  Returns:
    A weather.
  """
  await dnd.run_generate_weather(interaction)

@client.tree.command(name="list_weather", description="Get statistics relating to the weather command")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=3)
async def get_weather_list(interaction: QuoteBotInteraction):
  """
  Gets the weather_probabilities.json file, and outputs the list as an embed.
  Returns:
    Embed object containing data on weather_probabilities.json.
  """
  await dnd.run_weather_list(interaction)

@client.tree.command(name="reset_weather", description="Resets all weather counts to 0")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=1)
async def clear_weather_stats(interaction: QuoteBotInteraction):
  """
  Clears the weather_probabilities.json file, puts all counts to 0.
  """
  await dnd.run_reset_weather_dict(interaction)

@client.tree.command(name="add_weather", description="Adds a new weather that to the generator")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@app_commands.describe(weather="The weather you want added")
@with_timeout(timeout=1)
async def add_weather(interaction: QuoteBotInteraction, weather : str):
  """
  Adds the 'weather' to the weather_probabilities.json file.
  Appended as data[weather] = 0.
  Args:
    weather: the weather to add to the .json file
  """
  await dnd.run_add_new_weather(interaction, weather)

@client.tree.command(name="remove_weather", description="Removes an existing weather")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@app_commands.describe(weather="The weather you want removed")
@with_timeout(timeout=1)
async def remove_weather(interaction: QuoteBotInteraction, weather : str):
  """
  Removes specified weather from the weather_probabilities.json file.
  Args:
    weather: the weather to remove completely from the .json file
  """
  await dnd.run_remove_weather(interaction, weather)

@client.tree.command(name="modify_weather", description="Modifies the count of an existing weather")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@app_commands.describe(weather="The weather you want to modify")
@app_commands.describe(new_count="The new number of times the weather has been rolled")
@with_timeout(timeout=2)
async def modify_weather(interaction: QuoteBotInteraction, weather: str, new_count: int):
  """
  Given weather, new_count, makes data[weather] = new_count.
  Modifies the weather to have the new_count as the value.
  Args:
    weather: the weather to modify the count of
    new_count: the new integer to set the count to
  """
  await dnd.run_modify_weather_counts(interaction, weather, new_count)

@client.tree.command(name="get_raw_weather_json", description="Outputs the raw json file")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=3)
async def output_raw_weather_json(interaction: QuoteBotInteraction):
  """
  Outputs the weather_probabilities json file as a downloadable.
  Returns:
    A .json object sent as a file
  """
  await dnd.run_output_json_file(interaction)

@client.tree.command(name="weather_statistics", description="Outputs the raw json file")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=2)
async def weather_statistics(interaction: QuoteBotInteraction):
  """
  Outputs statistics regarding the weather rolled.
  Returns:
    String that details: total rolls, percentages, most/least common
  """
  await dnd.run_weather_stats(interaction)

@client.tree.command(name="join", description="Joins the vc the user is in")
@with_timeout(timeout=2)
async def join(interaction: QuoteBotInteraction):
  """
  Bot joins the current vc the user is in.
  """
  await music.run_join(interaction)

@client.tree.command(name="leave", description="Disconnects me from a voice channel")
@with_timeout(timeout=2)
async def leave(interaction: QuoteBotInteraction):
  """
  Stops the music, if playing. Then disconnects.
  """
  await music.run_leave(interaction)

@client.tree.command(name="play", description="Play a youtube link")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@app_commands.describe(link="The query or link to a Youtube video")
@with_timeout(timeout=10)
async def play(interaction: QuoteBotInteraction, link: str):
  """
  Plays music specified by the user.
  
  Can accept links or queries.
  Args:
    link: the link/query the user inputs to play
  """
  await music.run_play(interaction, link)

@client.tree.command(name="skip", description="Skip the current song")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=3)
async def skip(interaction: QuoteBotInteraction):
  """
  Skips the current song playing from the queue.
  """
  await music.run_skip(interaction)

@client.tree.command(name="queue", description="Lists the songs in the queue")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=2)
async def list_queue(interaction: QuoteBotInteraction):
  """
  Lists the songs in the queue.
  Returns:
    A description of the current queue.
  """
  await music.run_list_queue(interaction)

@client.tree.command(name="clear_queue", description="Clears the songs queue")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=2)
async def clear_queue(interaction: QuoteBotInteraction):
  """
  Clears the queue of all songs.
  """
  await music.run_clear_queue(interaction)

@client.tree.command(name="pause", description="Pauses the current song")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=2)
async def pause(interaction: QuoteBotInteraction):
  """
  Pause the current song playing.
  """
  await music.run_pause(interaction)

@client.tree.command(name="resume", description="Resumes the currently paused song")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=2)
async def resume(interaction: QuoteBotInteraction):
  """
  Resumes if the song is paused.
  """
  await music.run_resume(interaction)

@client.tree.command(name="repeat", description="Repeatedly plays the current song")
@app_commands.guilds(*[discord.Object(id=id) for id in GUILD_IDS_PRIVATE])
@with_timeout(timeout=2)
async def repeat(interaction: QuoteBotInteraction):
  """
  Repeats the currently playing song.
  """
  await music.run_repeat(interaction)

@client.tree.command(name="random_msg", description="Get a random message from a given user's last 200 messages by default")
@app_commands.describe(user="The user to find a random message from")
@app_commands.describe(limit="Limit the number of messages sent, larger numbers will cause this to time out")
@app_commands.describe(min_count="If user sent < than min_count messages, this command will do nothing")
@with_timeout(timeout=7)
async def rand(interaction: QuoteBotInteraction, user : discord.Member, limit : Optional[int], min_count : Optional[int]):
  """
  Sends a random single text user sent in this server. quotes the user.
  Args:
    user: the user to find a quote of.
    limit: the number of previous messages to search through. May cause timeouts if too large.
    min_count: the min number of messages this user must have sent for this command to return a message. Defaulted
  
    Returns:
      A random message sent by a user in the last specified number of messages.
  """
  await quotes.run_rand(interaction, user, limit=limit, min_count=min_count)

@client.tree.command(name="repeat_after_me", description="Repeats what you say (no rude words you goober)")
@app_commands.describe(string="The string you want me to repeat")
@with_timeout(timeout=1)
async def repeat_after_me(interaction: QuoteBotInteraction, string: str):
    """
    Repeats whatever the user says.
    Args:
      string: user input to repeat
    Returns:
      string: whatever the user said
    """
    await quotes.run_repeat(interaction, string)

@client.tree.command(name="dice", description="Rolls a dice with a number of faces")
@app_commands.describe(faces="The number of faces this dice has")
@with_timeout(timeout=2)
async def dice(interaction: QuoteBotInteraction, faces: int, addon: Optional[int]):
  """
  Rolls a dice with die_num number of faces.
  Args:
    die_num: number of faces on this dice to roll
  Returns:
    The roll on the dice.
  """
  await utils.run_d(interaction, faces, addon)

# TODO: convert this to embedded links
@client.tree.command(name="timezone", description="Convert a time in a given timezone to another")
@app_commands.describe(time="Time at the origin city, HH:MM format")
@app_commands.describe(origin_country="The origin country, enter IANA-compliant continental name, e.g. America, not USA")
@app_commands.describe(origin_city="The origin city, enter IANA-compliant city name, e.g. Los Angeles")
@app_commands.describe(target_country="The country you to convert the time to, enter IANA-compliant continental name")
@app_commands.describe(target_city="The city you want to convert the time to, enter IANA-compliant city names")
@app_commands.describe(date_str="Optional date, if nothing entered, will use current date")
@with_timeout(timeout=3)
async def timezone(
  interaction: QuoteBotInteraction,
  time: str,
  origin_country: str,
  origin_city: str, 
  target_country: str,
  target_city: str,
  date_str: str | None = None
):
  """
  Converts a given timezone to a target timezone.
  Args:
    time: the current time you want converted, HH/MM
    origin_country: the country of the timezone you want converted
    origin_city: the city of the timezone you want converted
    target_country: the country of the timezone it converts into
    target_city: the city of the timezone it converts into
    date_str: optional. if none given, uses current system time. else
                given using DD/MM/YYYY format
  Returns:
    The converted time in a string format.
  """
  await utils.run_timezone_converter(
    interaction,
    time,
    origin_country,
    origin_city,
    target_country,
    target_city,
    date_str
  )

if __name__ == "__main__":
  # Runs the bot
  try:
    print("QuoteBot: Starting bot...")
    client.run(BOT_TOKEN)
  except Exception as e:
    report_error("error starting bot (are you connected to the internet?): ", e)
    print(f"[ERROR]: run bot: Are you connected to the internet?")
    print(e)
