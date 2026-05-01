from dataclasses import dataclass

@dataclass
class Song:
  title: str
  url: str
  song_length: int # seconds

  @property
  def format_duration(self) -> str:
    """
    Formats the duration as MM:SS, or if too long, HH:MM:SS
    """

    minutes, seconds = divmod(self.song_length, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
      return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"
