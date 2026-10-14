import pytest
import time

from datetime import datetime

from helpers.utility_helpers import current_year
from helpers.secret_santa_helpers import read_secret_santa_data, apply_reaction, PARTICIPANT_ADD, PARTICIPANT_REMOVE, ATTENDEE_ADD, ATTENDEE_REMOVE
from classes import guild_state as gs

@pytest.fixture
def guild():
  return gs.GuildState()


def make_data():
  return {
      "organiser": "Anti",
      "participants":[
        "A",
        "B",
        "C",
      ],
      "date": "05-12-2026",
      "attendees": [
        "D",
        "E"
      ]
    }

def test_current_year_correctly():
  """
  Test the current year utility func is correct.
  """
  actual_year = datetime.now().year
  assert current_year() == actual_year

def test_extract_data():
  """
  Correct extraction of data.
  """
  extracted = read_secret_santa_data(make_data())
  assert extracted["organiser"] == "Anti"
  assert extracted["participants"] == ["A", "B", "C"]
  assert extracted["date"] == "05-12-2026"
  assert extracted["attendees"] == ["D", "E"]

def test_reactions_participant():
  data = make_data()
  assert apply_reaction(data, "D", PARTICIPANT_ADD) is True
  assert data["participants"] == ["A", "B", "C", "D"]
  assert apply_reaction(data, "D", PARTICIPANT_REMOVE) is True
  assert data["participants"] == ["A", "B", "C"]

  assert apply_reaction(data, "C", ATTENDEE_ADD) is True
  assert data["attendees"] == ["E", "C"]
  assert apply_reaction(data, "C", ATTENDEE_REMOVE) is True
  assert data["attendees"] == ["E"]

def test_case_insensitive():
  data = make_data()
  assert apply_reaction(data, "a", PARTICIPANT_ADD) is False
  assert data["participants"] == ["A", "B", "C"]

def test_ignore_unknown_emojis():
  data = make_data()
  assert apply_reaction(data, "A", "👍") is False

def test_missing_keys_create():
  data = {}
  assert apply_reaction(data, "A", PARTICIPANT_ADD) is True
  assert data == {"participants": ["A"], "attendees": []}
