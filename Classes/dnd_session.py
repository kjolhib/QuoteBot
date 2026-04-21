from classes.dice import Dice
from helpers.DiceHelpers import check_die_faces
from exceptions.dice import too_many_dice_error
from exceptions.dice import die_alr_exists_error, no_dice_in_sesh_error, invalid_faces_error

class DnDSession:
  """
  A DnD session class. Stores information about the current session.
  """
  def __init__(self):
    self.is_active: bool = False
    self.start_time : float = 0
    self.current_session_dice : list[Dice] = []

  def create_new_dice(self, faces: int, scenario: str) -> None:
    self.verify_session_die_creation(scenario, faces) # raises error if scenario is invalid, or too many dice
    new_dice = Dice(scenario, int(faces))
    self.current_session_dice.append(new_dice)

  def remove_dice(self, scenario: str) -> None:
    die = self.verify_session_die_exists(scenario)
    if not die:
      raise no_dice_in_sesh_error.NoDiceInSeshError
    
    self.current_session_dice = [d for d in self.current_session_dice if d.scenario != scenario]

  def list_dice(self) -> str:
    """
    Lists the dice in the current session.
    """
    if not self.current_session_dice:
      raise no_dice_in_sesh_error.NoDiceInSeshError("No dice in session.")
    
    print_msg = "**__Dice Created__:**\n"
    for die in self.current_session_dice:
      print_msg += f"**{die.scenario}**: D**{die.faces}**\n"

    return print_msg
  
  def verify_session_die_exists(self, scenario: str) -> Dice | None:
    """
    Verifies that a die with the same scenario exists.
    Returns:
      - the die if it exists
      - None if it does not exist
    """
    return next((d for d in self.current_session_dice if d.scenario == scenario), None)

  def verify_session_die_creation(self, scenario: str, faces: int) -> None:
    """
    Verifies:
      - a die with the same scenario does not already exist
      - there are not too many dice in the session
      - faces == 4 || faces >= 6
    """
    if not check_die_faces(faces):
      raise invalid_faces_error.InvalidFacesError
    
    if len(self.current_session_dice) >= 100:
      raise too_many_dice_error.TooManyDiceError(f"Too many die! There's over 100 dies here! How did you even create this many?!")

    if isinstance(self.verify_session_die_exists(scenario), Dice):
      raise die_alr_exists_error.DieAlrExistsError(f"Dice with this scenario name: {scenario}, already exists.")

