import pytest

from classes.dnd_session import DnDSession
from exceptions.dice import (
  die_alr_exists_error,
  invalid_faces_error,
  no_die_in_sesh_error,
  too_many_dice_error
)

"""
session: the current DnDSession class
Testing various commands relating to sessions
"""

@pytest.fixture
def session():
  return DnDSession()

@pytest.fixture
def session_with_die(session: DnDSession):
  session.create_new_die("a", 6)
  return session

"""
Init tests
"""
def test_initial_dice_empty(session: DnDSession):
  assert not session.current_session_dice

def test_initial_inactive(session: DnDSession):
  assert not session.is_active

def test_initial_start_time(session: DnDSession):
  assert session.start_time == 0

"""
new_die
"""
def test_new_die_valid(session_with_die: DnDSession):
  assert session_with_die.current_session_dice
  assert len(session_with_die.current_session_dice) == 1

@pytest.mark.parametrize("faces", [1, 2, 3, 5])
def test_new_die__num_invalid(session: DnDSession, faces: int):
  with pytest.raises(invalid_faces_error.InvalidFacesError):
    session.create_new_die("a", faces)

def test_new_die__alr_exists(session_with_die: DnDSession):
  with pytest.raises(die_alr_exists_error.DieAlrExistsError):
    session_with_die.create_new_die("a", 6)

def test_new_die__too_many(session: DnDSession):
  for i in range(25):
    session.create_new_die(f"{i}", 7)

  assert len(session.current_session_dice) == 25

  with pytest.raises(too_many_dice_error.TooManyDiceError):
    session.create_new_die("101", 7)

"""
remove_die
"""
def test_remove_die_valid(session_with_die: DnDSession):
  assert session_with_die.current_session_dice
  assert len(session_with_die.current_session_dice) == 1

  session_with_die.remove_die("a")
  assert not session_with_die.current_session_dice

def test_remove_die__no_scenario(session_with_die: DnDSession):
  with pytest.raises(no_die_in_sesh_error.NoDieInSeshError):
    session_with_die.remove_die("b")
