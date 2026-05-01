import discord

from classes.guild_state import GuildState
from interaction_type import QuoteBotInteraction
from helpers.UtilityHelpers import safe_send, safe_edit
from exceptions.voice import no_voice_error, not_playing_error

class MusicInteractiveView(discord.ui.View):
  """
  For when /queue is called, creates an interactable view.
  
  Supports the following commands:
    - Pause
    - Resume
    - Skip
    - Clear
    - Repeat
  """
  def __init__(self, state: GuildState):
    super().__init__(timeout=60)
    self.state: GuildState = state
    self.message: discord.Message | None = None
    self._update_buttons()

  def _update_buttons(self):
    """
    Updates the buttons depending on whatever is played.

    Re-syncs the visual state of all buttons after any interaction was pressed.
    """
    vc = self.state.voice_client

    # if vc is none, require already playing and in vc
    is_playing = vc and vc.is_playing()
    is_paused = vc and vc.is_paused()

    self.pause_resume.label = "⏸" if is_paused else "▶"
    self.pause_resume.style = (discord.ButtonStyle.blurple if is_paused else discord.ButtonStyle.green)
    self.pause_resume.disabled = not (is_playing or is_paused)
    self.skip.disabled = not is_playing
    self.repeat.style = (discord.ButtonStyle.green if self.state.repeat else discord.ButtonStyle.grey)

  @discord.ui.button(label="⏯", style=discord.ButtonStyle.blurple, row=0)
  async def pause_resume(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicInteractiveView"]):
    """
    Creates the pause/resume buttons.
    
    They flip-flop between the 2, if paused, it shows resume as green, and if playing, it shows pause as red.
    """
    vc = self.state.voice_client
    if not vc:
      raise no_voice_error.NoVoiceClientError("Not in a voice channel. Add me to a voice first!", "MusicInteractiveView/pause_resume", "attempted to interact with pause/resume. However, voice client was None. Perhaps the bot disconnected from the VC in the middle of the command being pressed?")
    if vc.is_paused():
      vc.resume()
    elif vc.is_playing():
      vc.pause()

    self._update_buttons()
    await safe_edit(interaction, embed=self.state.q_to_embed(), view=self)

  @discord.ui.button(label="⏭", style=discord.ButtonStyle.blurple, row=0)
  async def skip(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicInteractiveView"]):
    """
    Creates the skip button.
    """
    vc = self.state.voice_client
    if not vc or not vc.is_playing():
      raise not_playing_error.NotPlayingError("Nothing playing to skip.")
    
    # trigger next song in queue
    vc.stop()
    await safe_send(interaction, "Skipping song...", ephemeral=True)

  @discord.ui.button(label="🗑️", style=discord.ButtonStyle.red, row=0)
  async def clear(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicInteractiveView"]):
    """
    Creates clear button.
    """
    await self.state.clear_queue()
    self._update_buttons()
    await safe_edit(interaction, embed=self.state.q_to_embed(), view=self)

  @discord.ui.button(label="🔁︎", style=discord.ButtonStyle.grey, row=0)
  async def repeat(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicInteractiveView"]):
    """
    Creates repeat button.
    """
    # Check something is playing
    if not self.state.current:
      raise not_playing_error.NotPlayingError("Nothing playing to repeat.")
    self.state.repeat = not self.state.repeat
    self._update_buttons()
    await safe_edit(interaction, embed=self.state.q_to_embed(), view=self)
  
  async def on_timeout(self):
    """
    Disables all buttons when the view expires after 60 seconds
    """
    await self.expire_cleanup("*Controls have expired after 60 seconds.*")

  async def expire_cleanup(self, reason: str):
    """
    Disables all buttons when:
      - 60 seconds have passed
      - no songs are playing
    
    Args:
      reason: the reason as to why this cleanup was called. Currently only if 60 seconds timeout, or queue is empty.
    """
    # stop timeout timer
    self.stop()
    
    print("[QUEUE VIEW]: timeout reached, disabling...")
    
    # disable all buttons
    for item in self.children:
      item.disabled = True # type: ignore
    
    # If the message still exists, update it
    if self.message:
      print("[QUEUE VIEW]: updating original message...")
      embed = discord.Embed(title="Nothing playing.")

      # Add onto the embed based on the following:
      if self.state.current:
        # If a song is playing:
        embed = discord.Embed(title=f"Now Playing: ", description=f"**{self.state.current.title}** [{self.state.current.format_duration}]")
      
      if len(self.state.queue) > 0 and self.state.current:
        # If the queue is not empty.
        # Current should also never be None.
        queue_str = "\n".join(f"`{i}`. {song.title} [{song.format_duration}]" for i, song in enumerate(self.state.queue, start=1))
        embed.add_field(name="Queue: ", value=queue_str, inline=False)


      embed.set_footer(text=reason)
      await self.message.edit(embed=embed, view=self)
      
