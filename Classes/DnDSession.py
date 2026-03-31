from .Dice import Dice

class DnDSession:
  is_active: bool = False
  start_time : int = 0
  current_session_dies : list[Dice] = []
