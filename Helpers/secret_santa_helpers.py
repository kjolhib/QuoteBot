import asyncio
import glob
import json
import os
import discord
from typing import Optional

SANTA_DIR = "data/secret_santa"

PARTICIPANT_ADD = "✅"
PARTICIPANT_REMOVE = "❌"
ATTENDEE_ADD = "🎉"
ATTENDEE_REMOVE = "👋"
SANTA_EMOJIS = [PARTICIPANT_ADD, PARTICIPANT_REMOVE, ATTENDEE_ADD, ATTENDEE_REMOVE]

santa_lock = asyncio.Lock()  # stops two quick reactions overwriting each other

def load_santa_file(year: int) -> dict:
  """
  Loads secret santa file with json loads.
  """
  with open(f"{SANTA_DIR}/{year}.json", "r") as f:
    return json.load(f)

def save_santa_file(year: int, data: dict) -> None:
  """
  Saves new data.
  """
  with open(f"{SANTA_DIR}/{year}.json", "w") as f:
    json.dump(data, f, indent=2)

def find_year_by_message(message_id: int) -> Optional[int]:
  """
  Returns the year by a message.
  """
  for path in glob.glob(f"{SANTA_DIR}/*.json"):
    with open(path, "r") as f:
      if json.load(f).get("message_id") == message_id:
        return int(os.path.splitext(os.path.basename(path))[0])
  return None


def _add(entries: list, name: str) -> bool:
  """
  Add a name to the entries.
  Returns:
    True: if name was added, False otherwise
  """
  if any(e.lower() == name.lower() for e in entries):
    return False
  entries.append(name)
  return True

def _remove(entries: list, name: str) -> bool:
  """
  Removes name from entries. 
  Returns:
    True: if name was removed, False otherwise
  """
  for e in entries:
    if e.lower() == name.lower():
      entries.remove(e)
      return True
  return False

def apply_reaction(data: dict, display_name: str, emoji: str) -> bool:
  """
  Mutates data. 
  Returns:
    True: if anything changed, False otherwise
  """
  # extract data
  participants = data.setdefault("participants", [])
  attendees = data.setdefault("attendees", [])

  if emoji == PARTICIPANT_ADD:
    moved = _remove(attendees, display_name)
    return _add(participants, display_name) or moved
  if emoji == PARTICIPANT_REMOVE:
    return _remove(participants, display_name)
  if emoji == ATTENDEE_ADD:
    moved = _remove(participants, display_name)
    return _add(attendees, display_name) or moved
  if emoji == ATTENDEE_REMOVE:
    return _remove(attendees, display_name)
  return False

def read_secret_santa_data(data) -> dict:
  """
  Reads secret santa data and converts it to a dictionary.
  """
  return {
    "date": data.get("date"),
    "organiser": data.get("organiser"),
    "participants": data.get("participants"),
    "attendees": data.get("attendees")
  }

def secret_santa_data_to_embed(data):
  """
  Converts raw json data into a discord embed.
  """
  extracted_data = read_secret_santa_data(data)
  embed = discord.Embed(title=f"{extracted_data['date'][-4:]} Secret Santa" if extracted_data['date'] else "Unknown data found.")
  embed.add_field(name="Organised by:", value=f"{extracted_data['organiser']}" if extracted_data['organiser'] else "Unknown Organiser", inline=False)
  embed.add_field(name="Expected Date:", value=f"{extracted_data['date']}" if extracted_data['date'] else "Unknown Date", inline=False)

  participants = "\n".join(f"`{i}`. {participant}" for i, participant in enumerate(extracted_data['participants'], start=1))
  embed.add_field(name="Participants: ", value=participants, inline=False)

  attendees = "\n".join(f"`{i}`. {attendee}" for i, attendee in enumerate(extracted_data['attendees'], start=1))
  embed.add_field(name="Attendees",value=attendees, inline=False)
  embed.set_footer(text="✅ join the draw · ❌ leave the draw · 🎉 attending only · 👋 not attending")
  return embed
  
