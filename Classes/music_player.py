import discord

from classes.protocols import MusicStateProtocol
from interaction_type import QuoteBotInteraction
from helpers.utility_helpers import safe_send, safe_edit
from exceptions.voice import no_voice_error, not_playing_error

class MusicPlayer(discord.ui.View):
  """
  For when /queue is called, creates an interactable view.
  
  Supports the following commands:
    - Pause
    - Resume
    - Skip
    - Clear
    - Repeat

  Attributes:
    `state`: a protocol that exposes
    `message`: the view that `/queue` creates. Maintained and continually updates the original view message, if not expired.
    `_update_buttons()`: updates and syncs the buttons whenever a buttone is pressed.
  """
  def __init__(self, state: MusicStateProtocol):
    super().__init__(timeout=60)
    self.state: MusicStateProtocol = state
    self.message: discord.Message | None = None
    self._update_buttons()

  def _update_buttons(self, force_playing: bool = False) -> None:
    """
    Updates the buttons depending on whatever is played.

    Re-syncs the visual state of all buttons after any interaction was pressed.
    """
    vc = self.state.voice_client

    # if vc is none, require already playing and in vc.
    # Force playing is to make sure that whenever we skip, or whenever update_buttons is dependent on play_next_song, 
    # the buttons will not be disabled in the time it takes for the next song to load and play.
    # This is here because of the fact that `vc.play()` is non-blocking.`
    is_playing = force_playing or (vc and vc.is_playing())
    is_paused = not force_playing and (vc and vc.is_paused())

    self.pause_resume.label = "▶" if is_paused else "⏸"
    # green when paused, grey when playing
    self.pause_resume.style = (discord.ButtonStyle.green if is_paused else discord.ButtonStyle.primary)
    self.pause_resume.disabled = not (is_playing or is_paused)
    self.skip.disabled = not is_playing
    self.loop.style = (discord.ButtonStyle.green if self.state.loop else discord.ButtonStyle.primary)

  @discord.ui.button(label="⏯", style=discord.ButtonStyle.primary, row=0)
  async def pause_resume(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicPlayer"]) -> None:
    """
    Pause/Resume buttons that pauses or skips the current song. Same functionality as their respective commands.
    
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

  @discord.ui.button(label="⏭", style=discord.ButtonStyle.primary, row=0)
  async def skip(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicPlayer"]) -> None:
    """
    Skip button that skips the song. Same functionality as `/skip` command.

    Raises:
      NotPlayingError: the bot is not playing anything, so there's nothing to skip.
    """
    vc = self.state.voice_client
    if not vc or not vc.is_playing():
      raise not_playing_error.NotPlayingError("Nothing playing to skip.")
    
    # trigger next song in queue
    vc.stop()
    self._update_buttons()

    await safe_send(interaction, "Skipping song...", ephemeral=True)

  @discord.ui.button(label="🗑️", style=discord.ButtonStyle.red, row=0)
  async def clear(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicPlayer"]) -> None:
    """
    Button that clears the queue. Same functionality as `/clear_queue` command.
    """
    await self.state.clear_queue()
    self._update_buttons()
    await safe_edit(interaction, embed=self.state.q_to_embed(), view=self)

  @discord.ui.button(label="🔁︎", style=discord.ButtonStyle.blurple, row=0)
  async def loop(self, interaction: QuoteBotInteraction, _: discord.ui.Button["MusicPlayer"]) -> None:
    """
    A button that sets repeat to `True`. Same functionality as `/loop` command.

    Raises:
      NotPlayingError: there are no songs playing or none in t
    """
    # Check something is playing
    if not self.state.current:
      raise not_playing_error.NotPlayingError("Nothing playing to loop.")
    self.state.loop = not self.state.loop
    self._update_buttons()
    await safe_edit(interaction, embed=self.state.q_to_embed(), view=self)
  
  async def on_timeout(self) -> None:
    """
    Disables all buttons when the view expires after 60 seconds.
    """
    await self.expire_cleanup("*Controls have expired after 60 seconds.")

  async def expire_cleanup(self, reason: str) -> None:
    """
    Disables all buttons when:
      - 60 seconds have passed
      - no songs are playing
    
    Edits all active views to a specified `reason` for cleanup.
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
      
  async def edit_view(self, embed: discord.Embed, force_playing: bool = False) -> None:
    """
    Edits the current view.

    Force playing is to prevent the `_update_buttons` from disabling the pause and resume buttons.
    
    This is only `True` in the case of `play_next_song`, which guarantees that if this function is called, then there will be a next song to play.

    Ie. `repeat` = `True`, or `queue` is not empty

    Args:
      embed: the newly updated embed to edit this view into
      force_playing: whether or not this edit is called from a command that guarantees a song will play next. If guranteed (ie. /skip), it will be `True`, and `_update_buttons` will not disable the pause/resume buttons. 
    """
    # update the buttons. This is to prevent the play/skip buttons from being disabled after the skip button was called.
    # Fprce playing is to prevent non-blocking nature of vc.play() to make the player "think" that there is no song playing,
    # when in reality, it's in between stopping the current song and playing the next one.
    self._update_buttons(force_playing=force_playing)
    if self.message:
      await self.message.edit(embed=embed, view=self)
