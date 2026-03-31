import discord
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import app_commands
from typing import Optional

# Helper Imports
from Commands import Utils, DnD, Quotes
from Helpers.Utility_helpers import safe_send, with_timeout
from Classes import DnDSession
from ErrorHandler import ErrorHandler

load_dotenv()
BOT_TOKEN = os.getenv("QBOT_TOKEN")
if not BOT_TOKEN:
  raise ValueError("Bot token is not set in environment.")
CMD_CHANNEL_ID = int(os.getenv("GHIONCK_CMD_CHNL"))
GUILD_IDS = [
  int(os.getenv("DEV_SERVER")),
  int(os.getenv("GHIONCK"))
]
MAX_SESSION_TIME_MINS = 60

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
  print(f'QuoteBot: {client.user} started!')
  for guild_id in GUILD_IDS:
    try:
      # get guild object
      guild = discord.Object(id=guild_id)

      # give global access to all commands
      client.tree.copy_global_to(guild=guild)
      synced = await client.tree.sync(guild=guild)
      print(f"[SYNC] Synced {len(synced)} commands to guild {guild_id}")
    except Exception as e:
      err = ErrorHandler.Error(f"syncing commands to guild {guild}: {e}", "sync")
      ErrorHandler.report_error(err)
      # print(f"[ERROR] syncing commands to guild {guild}: {e}")
    # await channel.send("QuoteBot is now online.")

# TODO: implement a loop that checks session active timer
# Loop time active
# @tasks.loop(minutes=MAX_SESSION_TIME_MINS, count=1)
# async def break_reminder():
#   channel = client.get_channel(CMD_CHANNEL_ID)
#   await channel.send(f"Take a break! You've been active for {MAX_SESSION_TIME_MINS} minutes!")

# Only loop if sessio is active
# @break_reminder.before_loop
# async def before__break_reminder():
#   if session.is_active:
#     await break_reminder()


@client.tree.command(name="start", description="Starts a DnD session")
@with_timeout(timeout=1)
async def start(interaction : discord.Interaction):
  """
  Start a DnD session.
  Sets is_active to be True in DnD class
  """
  await DnD.run_start(interaction)

@client.tree.command(name="end", description="End a DnD session")
@with_timeout(timeout=1)
async def end(interaction: discord.Interaction):
  """
  Ends a DnD session.
  Sets is_active to be False in DnD Class
  """
  await DnD.run_end(interaction)

@client.tree.command(name="new_dice", description="Creates a new dice instance with a scenario, with its own weights (advanced dnd shi)")
@app_commands.describe(scenario="What do you want to use this dice for?")
@app_commands.describe(faces="The number of faces this dice has")
@with_timeout(timeout=3)
async def new_dice(interaction: discord.Interaction, scenario: str, faces: int):
  """
  Creates a new dice instance named scenario with die_num number of faces
  Params:
    - scenario: the scenario the dice would be used in, is weighted
    - die_num: the number of faces this dice has. num != 4 and num > 5
  """
  await DnD.run_new_dice_instance(interaction, scenario, faces)

@client.tree.command(name="instance_dice", description="Roll an existing scenario dice")
@app_commands.describe(scenario="The dice you want to roll")
@app_commands.describe(addon="Adds or subtracts this result from the dice result")
@with_timeout(timeout=2)
async def s_dice(interaction: discord.Interaction, scenario: str, addon: Optional[int]):
  """
  Takes a scnenario, and rolls the corresponding scenario's dice
  :params scneario: the scenario that dictates the dice
  """
  await DnD.run_scenario_dice(interaction, scenario, addon)

@client.tree.command(name="list_die", description="Lists all the instances of dice")
@with_timeout(timeout=2)
async def list_dice(interaction: discord.Interaction):
  """
  Lists all the dice created
  """
  await DnD.run_list_dice(interaction)

@client.tree.command(name="weather", description="Generate a random weather")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=1)
async def generate_weather(interaction: discord.Interaction):
  """
  Generates a random weather using weighted chances.
  Stored in QuoteBot/Commands/weather_probabilities.json
  """
  await DnD.run_generate_weather(interaction)

@client.tree.command(name="weather_stats", description="Get statistics relating to the weather command")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=1)
async def get_weather_stats(interaction: discord.Interaction):
  """
  Gets the 'weather_probabilities' .json file, and outputs statistics.
  """
  await DnD.run_weather_stats(interaction)

@client.tree.command(name="reset_weather", description="Resets all weather counts to 0")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=1)
async def clear_weather_stats(interaction: discord.Interaction):
  """
  Clears the 'weather_probabilities' .json file, puts all counts to 0
  """
  await DnD.run_clear_weather_dict(interaction)

@client.tree.command(name="add_weather", description="Adds a new weather that to the generator")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@app_commands.describe(weather="The weather you want added")
@with_timeout(timeout=1)
async def add_weather(interaction: discord.Interaction, weather : str):
  """
  Adds the 'weather' to the weather_probabilities.json file.
  Appended as data[weather] = 0
  """
  await DnD.run_add_new_weather(interaction, weather)

@client.tree.command(name="remove_weather", description="Removes an existing weather")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@app_commands.describe(weather="The weather you want removed")
@with_timeout(timeout=1)
async def remove_weather(interaction: discord.Interaction, weather : str):
  """
  Removes 'weather' from the weather_probabilities.json file.
  """
  await DnD.run_remove_weather(interaction, weather)

@client.tree.command(name="modify_weather", description="Modifies the count of an existing weather")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@app_commands.describe(weather="The weather you want to modify")
@app_commands.describe(new_count="The new number of times the weather has been rolled")
@with_timeout(timeout=1)
async def modify_weather(interaction: discord.Interaction, weather : str, new_count : int):
  """
  Given weather, new_count, makes data[weather] = new_count.
  Modifies the weather to have the new_count as the value
  """
  await DnD.run_modify_weather_counts(interaction, weather, new_count)

@client.tree.command(name="get_raw_weather_json", description="Outputs the raw json file")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=3)
async def output_raw_weather_json(interaction):
  """
  Outputs the weather_probabilities json file as a downloadable
  """
  await DnD.run_output_json_file(interaction)

# Joins vc
@client.tree.command(name="join", description="Joins the vc the user is in")
@with_timeout(timeout=3)
async def join(interaction):
  """
  Bot joins the current vc the user is in.
  """
  await Utils.run_join(interaction)

@client.tree.command(name="leave", description="Disconnects me from a voice channel")
@with_timeout(timeout=3)
async def leave(interaction: discord.Interaction):
  """
  Stops the music, if playing. Then disconnects.
  """
  await Utils.run_leave(interaction)

@client.tree.command(name="play", description="Play a youtube link")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@app_commands.describe(link="The exact youtube URL")
@with_timeout(timeout=20)
async def play(interaction: discord.Interaction, link: str):
  """
  Plays music given by the user. Can accept links or queries.
  Params:
    - link: the link/query the user inputs to play
  """
  await Utils.run_play(interaction, link)

@client.tree.command(name="skip", description="Skip the current song")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=3)
async def skip(interaction: discord.Interaction):
  """
  Skips the current song playing from the queue.
  """
  await Utils.run_skip(interaction)

@client.tree.command(name="queue", description="Lists the songs in the queue")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=2)
async def list_queue(interaction: discord.Interaction):
  """
  Lists the songs in the queue
  """
  await Utils.run_list_queue(interaction)

@client.tree.command(name="pause", description="Pauses the current song")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=2)
async def pause(interaction: discord.Interaction):
  """
  Pause the current song playing
  """
  await Utils.run_pause(interaction)

@client.tree.command(name="resume", description="Resumes the currently paused song")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=2)
async def resume(interaction: discord.Interaction):
  """
  Resumes if the song is paused
  """
  await Utils.run_resume(interaction)

@client.tree.command(name="repeat", description="Repeatedly plays the current song")
@app_commands.guilds(
  discord.Object(id=GUILD_IDS[0]),
  discord.Object(id=GUILD_IDS[1])
)
@with_timeout(timeout=2)
async def repeat(interaction: discord.Interaction):
  """
  Repeats the currently playing song
  """
  await Utils.run_repeat(interaction)

@client.tree.command(name="random_msg", description="Get a random message from a given user's last 200 messages by default")
@app_commands.describe(user="The user to find a random message from")
@app_commands.describe(limit="Limit the number of messages sent, larger numbers will cause this to time out")
@app_commands.describe(min_count="If user sent < than min_count messages, this command will do nothing")
@with_timeout(timeout=7)
async def rand(interaction: discord.Interaction, user : discord.Member, limit : Optional[int], min_count : Optional[int]):
  """
  Sends a random single text user sent in this server. Quotes the user.
  :params user: the user to find a quote of
  """
  try:
    await Quotes.rand(interaction, user, limit=limit, min_count=min_count)
  except TimeoutError as t:
    print(f"Operation timed out: {t}")
    await safe_send(interaction, f"Operation has timed out on the last {limit} messages in this channel.")

@client.tree.command(name="repeat_after_me", description="Repeats what you say (no rude words you goober)")
@app_commands.describe(string="The string you want me to repeat")
@with_timeout(timeout=1)
async def repeatafterme(interaction: discord.Interaction, string: str):
    """
    Repeats whatever the user says.
    Params:
      - string: user input to repeat
    """
    await Quotes.run_repeat(interaction, string)

# Rolls a die, die faces specified by die_num
@client.tree.command(name="dice", description="Rolls a dice with a number of faces")
@app_commands.describe(faces="The number of faces this dice has")
@with_timeout(timeout=2)
async def d(interaction: discord.Interaction, faces: int, addon: Optional[int]):
  """
  Rolls a dice with die_num number of faces.
  Params:
    - die_num: number of faces on this dice to roll
  """
  await Utils.run_d(interaction, faces, addon)


@client.tree.command(name="timezone", description="Convert a time in a given timezone to another")
@app_commands.describe(time="Time at the origin city, HH:MM format")
@app_commands.describe(origin_country="The origin country, enter IANA-compliant continental name, e.g. America, not USA")
@app_commands.describe(origin_city="The origin city, enter IANA-compliant city name, e.g. Los Angeles")
@app_commands.describe(target_country="The country you to convert the time to, enter IANA-compliant continental name")
@app_commands.describe(target_city="The city you want to convert the time to, enter IANA-compliant city names")
@app_commands.describe(date_str="Optional date, if nothing entered, will use current date")
@with_timeout(timeout=3)
async def timezone(
  interaction: discord.Interaction,
  time: str,
  origin_country: str,
  origin_city: str, 
  target_country: str,
  target_city: str,
  date_str: str | None = None
):
  """
  Converts a given timezone to a target timezone.
  Params:
    - time: the current time you want converted, HH/MM
    - origin_country: the country of the timezone you want converted
    - origin_city: the city of the timezone you want converted
    - target_country: the country of the timezone it converts into
    - target_city: the city of the timezone it converts into
    - date_str: optional. if none given, uses current system time. else
                given using DD/MM/YYYY format
  """
  await Utils.run_timezone_converter(
    interaction,
    time,
    origin_country,
    origin_city,
    target_country,
    target_city,
    date_str
  )

# Runs the bot
try:
  client.run(BOT_TOKEN)
except Exception as e:
  print(f"[FATAL ERROR]: run bot: Are you connected to the internet?")
  print(e)
