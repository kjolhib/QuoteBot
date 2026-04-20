import datetime
import random
import discord
from typing import Optional

from Helpers.TimezoneHelpers import format_AEST
from Helpers.UtilityHelpers import safe_send, safe_send_embed, safe_send_file
from Helpers.DnDHelpers import *
from ErrorHandler.ErrorHandler import report_error
from Classes import GuildState as gs
from Classes import DnDSession as dsesh
from Classes import Dice as d

async def run_start(interaction: discord.Interaction):
  """
  Starts a DnD session.
  Creates one if not active.
  Sets the guild's dnd_session variable to the newly created class DnDSession.
  """
  state = gs.get_guild_state(str(interaction.guild_id))
  if state.dnd_session is not None:
    await safe_send(interaction, f"Session already started.")
    return
  
  # Create new class
  state.dnd_session = dsesh.DnDSession()
  state.dnd_session.is_active = True
  state.dnd_session.start_time = interaction.created_at.timestamp()
  human_readable_time = format_AEST(interaction.created_at, "%H:%M:%S")
  await safe_send(interaction, f"New session started at {human_readable_time}.")

async def run_end(interaction: discord.Interaction):
  """
  Ends a DnD session.
  Clears the guild's dnd_session.
  """
  state = gs.get_guild_state(str(interaction.guild_id))
  if state.dnd_session is None:
    await safe_send(interaction, f"No session is active.")
    return

  # How long the session lasted
  end_time = interaction.created_at.timestamp()
  duration = end_time - state.dnd_session.start_time
  human_readable_time = str(datetime.timedelta(seconds=duration))
  
  # Clear session
  state.dnd_session = None
  await safe_send(interaction, f"Session ended after {human_readable_time} seconds.")

async def run_new_die_instance(interaction: discord.Interaction, scenario: str, die_num: int):
  """
  Creates a new dice instance.
  If not active session, ignore.
  """
  state = gs.get_guild_state(str(interaction.guild_id))
  if state.dnd_session is None:
    await safe_send(interaction, f"Please only create instance die during a DnD session.")
    return

  if (die_num < 6 and die_num != 4):
    await safe_send(interaction, f"I do not know what a D{die_num} is. Choose a die that has either 4 or 6 or more faces ya bingus.")
    return

  curr_sesh_dies = state.dnd_session.current_session_dies

  for s in curr_sesh_dies:
    if (scenario == s.scenario):
      await safe_send(interaction, f"Dice with this scenarizo name: {scenario} already exists.")
      return
    
  if len(curr_sesh_dies) > 100:
    await safe_send(interaction, f"Too many die! There's over 100 dies here! How did you even create this many?!")
    return
  try:
    # Create new instance of dice with scenario and faces
    new_dice = d.Dice(scenario, int(die_num))
    curr_sesh_dies.append(new_dice)
    await safe_send(interaction, f"Created new dice of the __{scenario}__ (D**{die_num}**) scenario. There are now **{len(curr_sesh_dies)}** die in the session.")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while creating new die. Check logs for more details.")
    report_error(f"new_dice_instance", e, f"attempting to create new die with scenario: {scenario}, faces: {die_num}.")

async def run_scenario_die(interaction: discord.Interaction, scenario: str, addon: Optional[int]=0):
  """
  Given a specific DnD die name, roll it, with optional addon
  Params:
    - scenario: the name of the die
    - addon: optional. adds this value to the result of the die roll
  """
  state = gs.get_guild_state(str(interaction.guild_id))
  if state.dnd_session is None:
    await safe_send(interaction, f"No session is active.")
    return

  # Check that the scenario exists
  curr_sesh_dies = state.dnd_session.current_session_dies
  current_dice = next( # if a dice with scenario exists, set it, otherwise None
    (dice for dice in curr_sesh_dies if dice.scenario == scenario),
    None
  )

  # dice not found
  if not current_dice:
    await safe_send(interaction, f"No die of scenario **{scenario}** found. Please create one first using /new_dice.")
    return

  try:
    roll = current_dice.simulate_weighted_rolls()
  except Exception as e:
    await safe_send(interaction, f"Unknown error simulating the dice roll. Check logs for more details.")
    report_error(f"scenario_dice", e, f"attempting to simulate dice rolls for scenario {scenario}.")
    return

  # addon print msg
  # this took longer than i'd like to admit. 2am coding is such a vibe
  # TODO: probably look into this in the future to simplify logic
  if addon:
    addon_print = addon
    result = roll + addon
    sign = "+" if addon > 0 else "-"
    if addon_print < 0:
      addon_print = -addon_print
    print_msg = f"You have rolled a {roll} {sign} {addon_print} (stats) = **{result}** on {scenario} (D{current_dice.faces})."
  else:
    print_msg = f"You have rolled a **{roll}** on {scenario} (D{current_dice.faces})."

  await safe_send(interaction, print_msg)

async def run_list_dice(interaction: discord.Interaction):
  """
  Lists all scenario dice that exist.
  """
  # checks session active
  state = gs.get_guild_state(str(interaction.guild_id))
  if state.dnd_session is None:
    await safe_send(interaction, f"No session is active.")
    return
  
  curr_sesh_dies = state.dnd_session.current_session_dies
  if not curr_sesh_dies:
    # empty
    await safe_send(interaction, f"No dice exist.")
    return
  
  print_msg = "**Dice Created:**\n"
  for die in curr_sesh_dies:
    print_msg += f"__{die.scenario}__: D*{die.faces}*\n"

  await safe_send(interaction, print_msg)

async def run_generate_weather(interaction: discord.Interaction):
  """
  Generates a new weather from a json pool.
  The json is found in /weather_probabilities.json.
  """
  # Load weather. from DnD_helpers.py
  try:
    data: dict[str, int]= load_weather()

    weights: list[float] = []
    weathers: list[str] = []

    # Collect the information from the json, and weight each weather's probability by their counts.
    # More counts = less probability of being chosen.
    for weather, count in data.items():
      weathers.append(weather)
      weights.append(1/(count+1))

    # choose.
    chosen = random.choices(weathers, weights=weights, k=1)[0]
    data[chosen] += 1 # increment the count of the weather being chosen in the json file
    save_weather(data)
    await safe_send(interaction, f"The weather you have rolled is **{chosen}**! is that good?")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while loading/saving from weather json file. Check logs for more details.")
    report_error("generate_weather", e, "attempted to load/save weather data")

async def run_weather_stats(interaction: discord.Interaction):
  """
  Lists as an standard embed, the json file.
  Formatted as:
    <weather>
      <count>
    ...
  """
  try:
    data = load_weather()
    embed = discord.Embed.from_dict(data)

    for weather, count in data.items():
      embed.add_field(name=weather, value=str(count), inline=False)
    
    await safe_send_embed(interaction, embeds=embed)
  except Exception as e:
    await safe_send(interaction, "Unknown error occured while processing weather data. Check logs for more details.")
    report_error("weather_stats", e, "attempted to process weather data")

async def run_clear_weather_dict(interaction: discord.Interaction):
  """
  Resets the weather to default, defined as INIT_DATA in DnD_helpers.py
  """
  try:
    init_data = get_init_data()
    save_weather(init_data)
    await safe_send(interaction, "Weather data cleared.")
  except Exception as e:
    await safe_send(interaction, f"Unknown error occurred while clearing weather data. Check logs for more details.")
    report_error("clear_weather_dict", e, "attempted to clear weather data")

async def run_add_new_weather(interaction: discord.Interaction, weather: str):
  """
  Adds a new weather to weather_probabilities.json file.
  Persists across sessions.
  Does NOT modify INIT_DATA.
  """
  # TODO: allow for the newly added weather to "persist". ie. append it to INIT_DATA

  try:
    data = load_weather()
    data[weather] = 0
    save_weather(data)
    await safe_send(interaction, f"Weather '{weather}' has been added.")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while processing weather data. Check logs for more details.")
    report_error("add_new_weather", e, "attempted to add a new weather into the weather dict")

async def run_remove_weather(interaction: discord.Interaction, weather: str):
  """
  Removes weather from weather_probabilities.json file.
  Does NOT modify INIT_DATA
  """
  # TODO: allow for the removed weather to "persist". ie. delete it from INIT_DATA

  try:
    data = load_weather()
    if not weather in data:
      # weather to remove doesn't exist
      await safe_send(interaction, f"Weather {weather} is not a valid weather yet! Add it first with /add_weather!")
      return

    count = data[weather]
    del data[weather]
    save_weather(data)
    await safe_send(interaction, f"Weather {weather} removed with count {count}.")
  except Exception as e:
    await safe_send(interaction, f"Unknown error occurred while removing {weather}. Check logs for more details.")
    report_error(f"remove_weather", e, f"attempting to remove: {weather}.")
    return

async def run_modify_weather_counts(interaction: discord.Interaction, weather: str, new_count: int):
  """
  Modify the count of a given weather.
  Params:
    - weather: the name of the weather to be modified
    - new_count: the new count of the weather. weather.count = new_count
  """
  try:
    data = load_weather()
    if not weather in data:
      # weather to remove doesn't exist
      await safe_send(interaction, f"Weather {weather} is not a valid weather yet! Add it first with /add_weather!")
      return

    if new_count < 0:
      # negative count
      await safe_send(interaction, f"Negative counts ({new_count}) are not allowed you forehead. Try again.")
      return
    
    old_count = data[weather]
    data[weather] = new_count
    save_weather(data)
    await safe_send(interaction, f"Weather {weather} has been modified to have count {new_count}. Previous count was {old_count}")

  except Exception as e:
    await safe_send(interaction, f"Unknown error occurred when modifying weather: {weather}. Check logs for more details.")
    report_error(f"modify_weather", e, f"attempting to modify: {weather}.")

async def run_output_json_file(interaction: discord.Interaction) -> None:
  """
  Outputs the raw JSON file for storage if needed.
  """
  try:
    weather_path = get_weather_path()
    with open(f"{weather_path}", "rb") as f:
      file = discord.File(f, filename="weather_probabilities.json")
      await safe_send_file(interaction, file=file)

  except FileNotFoundError as fnfe:
    await safe_send(interaction, f"Error, weather_probabilities.json not found. @chewswisely fucked something up.")
    report_error("output_json_file", fnfe, "weather_probabilities.json file not found.")  
  except Exception as e:
    await safe_send(interaction, "Outputting file failed. Check logs for more details.")
    report_error("output_json_file", e, "attempting to output weather_probabilities.json file.")