from .Dice import Dice

class DnDSession:
  """
  A DnD session class. Stores information about the current session.
  """
  is_active: bool = False
  start_time : int = 0
  current_session_dies : list[Dice] = []
