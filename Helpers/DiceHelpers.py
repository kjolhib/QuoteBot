from random import randint

from exceptions.dice import invalid_faces_error

def compute_roll(die_num: int, addon: int | None=0) -> str:
  """
  Rolls a die.
  
  Given die_num faces, where `(die_num == 4) || (die_num >= 6)`, roll a die where addon is added to the result.
  Args:
    die_num: the faces of the die. Must be either exactly 4, or any number >= 6.
    addon: optional. The number added onto the result. Defaulted to 0.
  Returns:
    Whatever was rolled.
  Raises:
    InvalidFacesError: invalid number of faces specified.
  """
  if not check_die_faces(die_num):
    raise invalid_faces_error.InvalidFacesError(f"I do not know what a D{die_num} is. Choose a die that has either 4 or 6 or more faces ya bingus")
  
  # addon is optional, only added if specified by user
  if not addon:
    addon = 0

  roll = randint(1, die_num)
  if addon != 0:
    sign = "+" if addon > 0 else "-"
    return f"You have rolled a {roll} {sign} {abs(addon)} = **{roll + addon}** on a D{die_num}"
  
  return f"You have rolled a **{roll}** on a D{die_num}"

def check_die_faces(f: int) -> bool:
  """
  Check if the die faces is valid.
  
  Valid die faces are either exactly 4, or any number >= 6.
  """
  if (f < 6 and f != 4):
    return False
  return True
