from discord.embeds import Embed as de
from discord.colour import Colour as dc
from classes.dice import Dice
from helpers.dice_helpers import check_die_faces
from exceptions.dice import no_die_in_sesh_error, too_many_dice_error
from exceptions.dice import die_alr_exists_error, invalid_faces_error

class DnDSession:
  """
  A DnD session class.
  
  Stores information about the current session.

  Attributes:
    `is_active`: whether or not this session is active.
    `start_time`: the time the session started.
    `current_session_dice`: a list of all dice in the current session.
  """
  def __init__(self, is_active: bool = False, start_time: float = 0, csd: list[Dice] | None = None):
    self.is_active: bool = is_active
    self.start_time : float = start_time
    self.current_session_dice : list[Dice] = csd if csd else []

  def create_new_die(self, scenario: str, faces: int) -> None:
    """
    Creates a new die of a given scenario, with given faces.
    Args:
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
      The die if it exists, None otherwise.
    """
    return next((d for d in self.current_session_dice if d.scenario == scenario), None)

  def remove_die(self, scenario: str) -> None:
    """
    Removes the specified die from the session.

    Raises:
      NoDieInSeshError: if no die with specified scenario exists.
    """
    die = self.get_die(scenario)
    if not die:
      raise no_die_in_sesh_error.NoDieInSeshError(f"There is no die named {scenario} in current session ya bingus.")
    
    self.current_session_dice = [d for d in self.current_session_dice if d.scenario != scenario]

  def list_dice(self) -> de:
    """
    Lists the dice in the current session.
    Returns:
      String containing the dice:
      Format:
        Dice Created:
        {scenario}: D({faces})
        ...

    Raises:
      NoDieInSeshError: session does not have any dice created.
    """
    if not self.current_session_dice:
      raise no_die_in_sesh_error.NoDieInSeshError("No dice in session.")

    return self._to_embed()

  def _verify_die_creation(self, scenario: str, faces: int) -> None:
    """
    Verifies:
      - there are not too many dice in the session: `faces == 4 || faces >= 6`.
      - a die with the same scenario does not already exist.

    Raises:
      InvalidFacesError: non-valid faces specified.
      TooManyDiceError: more than 25 dice created in this session.
      DieAlrExistsError: a die with the specified scenario already exists.
    """
    if not check_die_faces(faces):
      raise invalid_faces_error.InvalidFacesError(f"I do not know what a D{faces} is. Choose a die that has either exactly 4 or >= 6 faces ya bingus.")
    
    if len(self.current_session_dice) >= 25:
      raise too_many_dice_error.TooManyDiceError(f"You cannot create more than 25 dice per session. Contact @chewswisely with a very good reason if you believe you somehow need more.")

    if isinstance(self.get_die(scenario), Dice):
      raise die_alr_exists_error.DieAlrExistsError(f"You lack originality. Die with this scenario name: **{scenario}**, already exists. Please think of an **original** scenario name.")

  def _to_embed(self) -> de:
    """
    Turns `current_session_dice` into an embed object for discord to send.
    """
    embed = de(title="**__Dice Created__:**", colour=dc.blue())
    for die in self.current_session_dice:
      embed.add_field(
        name=f"__{die.scenario}__",
        value=f"D(**{die.faces}**)",
        inline=False
      )
    
    return embed
