import random

class Dice:
  """
  A scenario dice.
  
  Stored by `DnDSession` class.

  Attributes:
    `scenario`: the string describing this die. It's unique identifier.
    `faces`: the number of faces on this die.
    `past_rolls`: a list containing the past rolls of this die.
  """
  def __init__(self, scenario: str, faces: int):
    self.scenario : str = scenario
    self.faces : int = faces
    self.past_rolls: list[int] = []

  def simulate_weighted_rolls(self) -> int:
    """
    Simulates weighted rolls on past rolls list.

    Returns:
      result: a randomly selected result.
    """
    # All possible faces
    possible = list(range(1, self.faces + 1))

    # All have equal weight
    weights = [1] * self.faces

    # If previous rolls exist, increase weight for last rolled number
    if self.past_rolls:
      last_roll = self.past_rolls[-1]
      weights[last_roll - 1] += 2

    result = random.choices(possible, weights=weights, k=1)[0]

    self.past_rolls.append(result)
    return result
