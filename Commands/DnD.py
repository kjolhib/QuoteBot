import discord
from typing import Optional

from interaction_type import QuoteBotInteraction

from exceptions.dice import die_alr_exists_error, invalid_faces_error, no_die_in_sesh_error
from helpers.TimezoneHelpers import format_AEST
from helpers.UtilityHelpers import safe_send, safe_send_embed, safe_send_file
from helpers.DnDHelpers import *
from exceptions.error_handler import report_error
from exceptions.dice import too_many_dice_error
from exceptions.dnd import weather_exists_error, weather_missing_error, weather_empty_error, negative_count_error
from exceptions.guild import null_session_error
from classes import weather_data as wd

async def run_start(interaction: QuoteBotInteraction):
  """
  Starts a DnD session.

  Creates one if not active. If already active, sends a relevant message saying so.
  Sets the guild's dnd_session variable to the newly created class DnDSession.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  if state.dnd_session is not None:
    await safe_send(interaction, f"Session already started.")
    return
  
  # Create new class
  state.start(interaction.created_at.timestamp())
  human_readable_time = format_AEST(interaction.created_at, "%H:%M:%S")
  await safe_send(interaction, f"New session started at {human_readable_time}.")

@require_valid_session
async def run_end(interaction: QuoteBotInteraction):
  """
  Ends a DnD session.

  Clears the guild's dnd_session.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  # Decorator makes sure a session is valid no matter what. If that somehow failed, this should catch it.
  assert state.dnd_session

  try:
    human_readable_time = state.end()
    await safe_send(interaction, f"Session ended after {human_readable_time} seconds.")
  except null_session_error.NullSessionError:
    await safe_send(interaction, f"Session ended, but ungracefully. Session was somehow ended before it even started. Check logs for more details.")
  except Exception as e:
    await safe_send(interaction, "Unknown error occurred. Check logs for more details.")
    report_error("run_end", e, "attempted to end session")

@require_valid_session
async def run_new_die(interaction: QuoteBotInteraction, scenario: str, die_num: int):
  """
  Creates a new dice instance.

  Requires dnd session to be active.
  Calls dnd_session's create_new_die.

  Args:
    scenario: the name of this dice, and usually at what time/instance it would be used in
    die_num: the number of faces on this die
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  assert state.dnd_session

  try:
    session = state.dnd_session
    session.create_new_die(die_num, scenario)
    await safe_send(interaction, f"Created new die of the **{scenario}** (D**{die_num}**) scenario. There are now **{len(session.current_session_dice)}** dice in the session.")
  except invalid_faces_error.InvalidFacesError:
    await safe_send(interaction, f"I do not know what a D{die_num} is. Choose a die that has either 4 or 6 or more faces ya bingus.")
  except die_alr_exists_error.DieAlrExistsError:
    await safe_send(interaction, f"You lack originality. Die with this scenario name: **{scenario}**, already exists. Please think of an **original** scenario name.")
  except too_many_dice_error.TooManyDiceError:
    await safe_send(interaction, f"Too many dice! There's over 100 dies here! How did you even create this many?!")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while creating new die. Check logs for more details.")
    report_error(f"new_dice_instance", e, f"attempting to create new die with scenario: {scenario}, faces: {die_num}.")

@require_valid_session
async def run_remove_die_instance(interaction: QuoteBotInteraction, scenario: str):
  """
  Removes a given die.

  Calls dnd_session's remove_die.

  Args:
    scenario: the die we want to remove from the current session

  Raises:
    NoDiceInSeshError: if the scenario doesn't exist in the current session
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  assert state.dnd_session

  try:
    state.dnd_session.remove_die(scenario)
    await safe_send(interaction, f"Dice, **{scenario}** removed. :o7: thanks for your service.")
  except no_die_in_sesh_error.NoDieInSeshError:
    await safe_send(interaction, f"No die of scenario **{scenario}** found.")
  except Exception as e:
    await safe_send(interaction, f"Unknown error occurred when removing dice.")
    report_error("run_remove_die_instace", e, f"attempted to remove dice of scenario {scenario}")

@require_valid_session
async def run_instance_die(interaction: QuoteBotInteraction, scenario: str, addon: Optional[int]=0):
  """
  Given a specific DnD die name, roll it, with optional addon.

  The addon is defaulted to 0. 
  The calculation is as follows: roll = choose_random(dice) + addon. Can accept negative addons.

  Args:
    scenario: the name of the die
    addon: optional. adds this value to the result of the die roll

  Returns:
    The roll + addon of the die.
  """
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  assert state.dnd_session

  # Check that the scenario exists
  session = state.dnd_session
  current_die = session.get_die(scenario)
  if not current_die:
    await safe_send(interaction, f"No die of scenario **{scenario}** found. Please create one first using /new_dice.")
    return
  
  try:
    roll = current_die.simulate_weighted_rolls()
  except Exception as e:
    await safe_send(interaction, f"Unknown error simulating the dice roll. This should never happen. Check logs for more details.")
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
    print_msg = f"You have rolled a {roll} {sign} {addon_print} (stats) = **{result}** on {scenario} (D{current_die.faces})."
  else:
    print_msg = f"You have rolled a **{roll}** on {scenario} (D{current_die.faces})."

  await safe_send(interaction, print_msg)

@require_valid_session
async def run_list_die(interaction: QuoteBotInteraction):
  """
  Lists all scenario die that exist.

  Returns:
    A list of die that the current session holds.

  Raises:
    NoDiceInSeshError: there are 0 dice created in the current session.
  """
  # checks session active
  state = interaction.client.get_guild_state(str(interaction.guild_id))
  assert state.dnd_session

  session = state.dnd_session
  try:
    print_msg = session.list_dice() # raises error if no dice in session
    await safe_send(interaction, print_msg)
  except no_die_in_sesh_error.NoDieInSeshError as e:
    await safe_send(interaction, str(e))
    return

@require_valid_session
async def run_generate_weather(interaction: QuoteBotInteraction):
  """
  Generates a new weather from a json pool.

  The json is found in data/weather_probabilities.json.

  Returns:
    A pseudo-randomly generated weather.

    Weighted by the more often it is chosen before, it less likely it'd be chosen again.

  Raises:
    WeatherEmptyError: there are no weathers to in the json.
  """
  try:
    data: wd.WeatherData= wd.load_weather()

    # choose.
    chosen = data.select_weighted_random()
    data.increment_val(chosen)
    wd.save_weather(data)
    await safe_send(interaction, f"The weather you have rolled is **{chosen}**! is that good?")
  except weather_empty_error.WeatherEmptyError:
    await safe_send(interaction, f"There are no weathers to choose! Add one with /add_weather or reset it with /reset_weather")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while loading/saving from weather json file. Check logs for more details.")
    report_error("generate_weather", e, "attempted to load/save weather data")

async def run_weather_list(interaction: QuoteBotInteraction):
  """
  Lists as an standard embed, the json file.
  
  Returns:
    A list of all the weathers and the times they've been rolled.

    Format:
      {
        weather: times_rolled,
        ...
      }
  """
  try:
    data= wd.load_weather()
    embed = data.list_to_embed()
    
    await safe_send_embed(interaction, embeds=embed)
  except Exception as e:
    await safe_send(interaction, "Unknown error occured while processing weather data. Check logs for more details.")
    report_error("weather_stats", e, "attempted to process weather data")

@require_valid_session
async def run_reset_weather_dict(interaction: QuoteBotInteraction):
  """
  Resets the weather to default, defined as INIT_DATA in weather_data.py.

  Raises:
    FileNotFoundError: data/weather_probabilities.json was not found. Should never happen in practice unless I accidentally deleted it.
  """
  try:
    wd.reset_json()
    await safe_send(interaction, "Weather data cleared.")
  except FileNotFoundError as fnfe:
    await safe_send(interaction, f"Weather probabilities JSON file was not found. Contact @chewswisely, he messed something up .^.")
    report_error("reset_weather_dict", fnfe, "attempted to clear the weather dictionary, but the file was not found")
  except Exception as e:
    await safe_send(interaction, f"Unknown error occurred while clearing weather data. Check logs for more details.")
    report_error("clear_weather_dict", e, "attempted to clear weather data")

@require_valid_session
async def run_add_new_weather(interaction: QuoteBotInteraction, weather: str):
  """
  Adds a new weather to weather_probabilities.json file.
  
  Persists across sessions.
  
  Does NOT modify INIT_DATA.

  Raises:
    WeatherExistsError: the weather already exists in the json.
  """
  # TODO: allow for the newly added weather to "persist". ie. append it to INIT_DATA

  try:
    data = wd.load_weather()
    data.add_new_weather(weather)
    wd.save_weather(data)
    await safe_send(interaction, f"Weather '{weather}' has been added.")
  except weather_exists_error.WeatherExistsError:
    await safe_send(interaction, f"Weather '{weather}' already exists!")
  except Exception as e:
    await safe_send(interaction, f"Unknown error while processing weather data. Check logs for more details.")
    report_error("add_new_weather", e, "attempted to add a new weather into the weather dict")

@require_valid_session
async def run_remove_weather(interaction: QuoteBotInteraction, weather: str):
  """
  Removes weather from weather_probabilities.json file.

  Does NOT modify INIT_DATA.

  Raises:
    WeatherMissingError: the weather to remove doesn't exist in the json.
  """
  # TODO: allow for the removed weather to "persist". ie. delete it from INIT_DATA

  try:
    data = wd.load_weather()

    count = data.remove_weather(weather)
    wd.save_weather(data)
    await safe_send(interaction, f"Weather '{weather}' removed with count **{count}**.")
  except weather_missing_error.WeatherMissingError:
    await safe_send(interaction, f"Weather '{weather}' is not a valid weather yet! Add it first with /add_weather!")
  except Exception as e:
    await safe_send(interaction, f"Unknown error occurred while removing {weather}. Check logs for more details.")
    report_error(f"remove_weather", e, f"attempting to remove: {weather}.")
    return

@require_valid_session
async def run_modify_weather_counts(interaction: QuoteBotInteraction, weather: str, new_count: int):
  """
  Modify the count of a given weather.

  Args:
    weather: the name of the weather to be modified.
    new_count: the new count of the weather. weather -> new_count.

  Raises:
    WeatherMissingError: weather to modify doesn't exist.
    NegativeCountError: the new_count is negative, a weather being rolled negative times doesn't make sense.
  """
  try:
    data = wd.load_weather()

    if new_count < 0:
      # negative count
      await safe_send(interaction, f"Negative counts ({new_count}) are not allowed you forehead. Try again.")
      return
    
    old_count = data.modify_weather(weather, new_count)
    wd.save_weather(data)
    await safe_send(interaction, f"Weather '{weather}' has been modified to have count **{new_count}**. Previous count was {old_count}.")
  except weather_missing_error.WeatherMissingError:
    await safe_send(interaction, f"Weather '{weather}' is not a valid weather yet! Add it first with /add_weather!")
  except negative_count_error.NegativeCountError:
    await safe_send(interaction, f"Counts cannot be negative: {new_count}. Choose a positive number.")
  except Exception as e:
    await safe_send(interaction, f"Unknown error occurred when modifying weather: {weather}. Check logs for more details.")
    report_error(f"modify_weather", e, f"attempting to modify: {weather}.")

async def run_output_json_file(interaction: QuoteBotInteraction) -> None:
  """
  Outputs the raw JSON file for storage if needed.

  Raises:
    FileNotFoundError: data/weather_probabilities.json isn't found
  """
  try:
    weather_path = wd.get_weather_path()
    with open(f"{weather_path}", "rb") as f:
      file = discord.File(f, filename="weather_probabilities.json")
      await safe_send_file(interaction, file=file)

  except FileNotFoundError as fnfe:
    await safe_send(interaction, f"Error, weather_probabilities.json not found. @chewswisely fucked something up.")
    report_error("output_json_file", fnfe, "weather_probabilities.json file not found.")  
  except Exception as e:
    await safe_send(interaction, "Outputting file failed. Check logs for more details.")
    report_error("output_json_file", e, "attempting to output weather_probabilities.json file.")

async def run_weather_stats(interaction: QuoteBotInteraction):
  """
  Returns statistics about the weather rolls.

  Outputs in embed format similarly to list_weather.

  Returns:
    An embed containing statistics:

    Formatted:
      total_rolls: int
      percentages: {weather: percentage_rolled}
      most_common: string
      least_common: string
  """
  try:
    data = wd.load_weather()

    stats = data.statistics()
    embed = stats.to_embed()

    await safe_send_embed(interaction, embed)

  except Exception as e:
    await safe_send(interaction, "Unknown error occurred. Check logs for more details")
    report_error("run_weather_stats", e, "attempted to run statistics on the weaather")
