import random

class Dice:
  def __init__(self, scenario, faces):
    self.scenario : str = scenario
    self.faces : int = faces
    self.past_rolls = []

  def simulate_weighted_rolls(self):
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