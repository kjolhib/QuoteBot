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

  def create_new_die(self, faces: int, scenario: str) -> None:
    """
    Creates a new die of a given scenario, with given faces.
    Params:
      - faces: the number of faces on this die
      - scenario: the name/identification of this die. Used for rolling this specific die
    """
    self._verify_die_creation(scenario, faces) # raises error if scenario is invalid, or too many dice
    new_dice = Dice(scenario, int(faces))
    self.current_session_dice.append(new_dice)

  def get_die(self, scenario: str) -> Dice | None:
    """
    Given a scenario, verifies that a die with the same scenario exists.
    Returns:
      - the die if it exists
      - None if it does not exist
    """
    return next((d for d in self.current_session_dice if d.scenario == scenario), None)

  def remove_die(self, scenario: str) -> None:
    die = self.get_die(scenario)
    if not die:
      raise no_dice_in_sesh_error.NoDiceInSeshError
    
    self.current_session_dice = [d for d in self.current_session_dice if d.scenario != scenario]

  def list_dice(self) -> str:
    """
    Lists the dice in the current session.
    Returns:
      - string containing the dice in the following format:
        Dice Created:
        {scenario}: D({faces})
        ...
    """
    if not self.current_session_dice:
      raise no_dice_in_sesh_error.NoDiceInSeshError("No dice in session.")
    
    print_msg = "**__Dice Created__:**\n"
    for die in self.current_session_dice:
      print_msg += f"**{die.scenario}**: D**{die.faces}**\n"

    return print_msg

  def _verify_die_creation(self, scenario: str, faces: int) -> None:
    """
    Verifies:
      - there are not too many dice in the session
      - faces == 4 || faces >= 6
      - a die with the same scenario does not already exist
    """
    if not check_die_faces(faces):
      raise invalid_faces_error.InvalidFacesError
    
    if len(self.current_session_dice) >= 100:
      raise too_many_dice_error.TooManyDiceError(f"Too many die! There's over 100 dies here! How did you even create this many?!")

    if isinstance(self.get_die(scenario), Dice):
      raise die_alr_exists_error.DieAlrExistsError(f"Dice with this scenario name: {scenario}, already exists.")
