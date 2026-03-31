###### REMOVE #######


import random
import time
import discord
from dataclasses import dataclass
from collections import deque

# class Dice:
#   def __init__(self, scenario, faces):
#     self.scenario : str = scenario
#     self.faces : int = faces
#     self.past_rolls = []

#   def simulate_weighted_rolls(self):
#     # All possible faces
#     possible = list(range(1, self.faces + 1))

#     # All have equal weight
#     weights = [1] * self.faces

#     try:
#       # If previous rolls exist, increase weight for last rolled number
#       if self.past_rolls:
#         last_roll = self.past_rolls[-1]
#         weights[last_roll - 1] += 2

#       result = random.choices(possible, weights=weights, k=1)[0]

#       self.past_rolls.append(result)
#       return result
#     except Exception as e:
#       print("CommandDrivers/Classes/sim_weighted_rolls errored")

# @dataclass
# class DnDSession:
#   is_active: bool = False
#   start_time : int = 0

# class Error:
#   def __init__(self, error_msg, func_name):
#     self.error_msg: str = error_msg
#     self.func_name: str = func_name
#     self.time = time.ctime(time.time())

# class GuildState:
#   def __init__(self):
#     self.queue: deque[tuple[str, str]] = deque() # Queue of the songs
#     """
#     Format of the queue:
#       {
#         guild_id: deque([
#           (youtube link: string, title: string),
#           ...
#         ])
#       }
#     """
#     self.voice_client: discord.VoiceClient | None = None
#     self.current: tuple[str, str] | None = None # current song, containing url, title
#     self.repeat: bool = False # repeats current song

