import pytest
import time

from classes import guild_state as gs

@pytest.fixture
def guild():
  return gs.GuildState()

@pytest.fixture
def guild_ds():
  g = gs.GuildState()
  g.start(time.time()) # just some random time
  return g

"""
Initialisation
"""
def test_empty_initialisation(guild: gs.GuildState):
  assert not guild.current
  assert not guild.dnd_session
  assert not guild.queue
  assert not guild.loop
  assert not guild.voice_client

"""
dnd_session initialisation
"""
def test_guild_dnd__valid(guild_ds: gs.GuildState):
  assert guild_ds.dnd_session
  assert not guild_ds.dnd_session.current_session_dice

def test_guild_dnd__end_valid(guild_ds: gs.GuildState):
  assert guild_ds.dnd_session
  guild_ds.end()
  assert not guild_ds.dnd_session
