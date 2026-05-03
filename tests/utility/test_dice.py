import pytest
from helpers.dice_helpers import compute_roll

from exceptions.dice import invalid_faces_error

"""
die_num: number of faces
Testing valid and invalid number of faces.
"""
@pytest.mark.parametrize("die_num", [1, 2, 3, 5, -2])
def test_roll_invalid_faces(die_num: int):
  with pytest.raises(invalid_faces_error.InvalidFacesError):
    compute_roll(die_num)

@pytest.mark.parametrize("die_num", [4, 6, 100])
def test_roll_valid_faces(die_num: int):
  result = compute_roll(die_num)
  assert f"D{die_num}" in result

"""
addon: adds onto the result
Tests positive, negative, and 0
"""

def test_positive_addon():
  result = compute_roll(6, addon=2)
  assert f"+" in result
  assert "2" in result

def test_negative_addon():
  result = compute_roll(6, addon=-2)
  assert f"-" in result
  assert "2" in result

def test_0_addon():
  result = compute_roll(6)
  assert "-" not in result
  assert "+" not in result
