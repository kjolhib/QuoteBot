import pytest
import time

from datetime import datetime

from helpers.utility_helpers import current_year
from helpers.secret_santa_helpers import read_secret_santa_data
from classes import guild_state as gs

@pytest.fixture
def guild():
  return gs.GuildState()


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
  dummy_data = {
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
  extracted = read_secret_santa_data(dummy_data)
  assert extracted["organiser"] == "Anti"
  assert extracted["participants"] == ["A", "B", "C"]
  assert extracted["date"] == "05-12-2026"
  assert extracted["attendees"] == ["D", "E"]

