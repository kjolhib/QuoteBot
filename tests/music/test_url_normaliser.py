import pytest

from helpers.music_helpers import normalise_yt_url # type: ignore

"""
Testing the youtube link normaliser found in music_helpers.py.

Standard link:
  https://www.youtube.com/watch
"""

RR = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
RR_SHARE = "https://youtu.be/dQw4w9WgXcQ?si=BwEdLZx8HWuMztxa"
RR_SHORT = "https://www.youtube.com/shorts/g2vo6NWdDPc"
RR_SHORT_SHARE = "https://youtube.com/shorts/g2vo6NWdDPc?si=j5D4d8qb8IqNuAqF"
RR_MOBILE = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"

@pytest.mark.parametrize("url", [RR, RR_SHARE, RR_SHORT, RR_SHORT_SHARE, RR_MOBILE])
def test_variants_to_standard(url: str):
  result, is_url = normalise_yt_url(RR)
  assert result == RR and is_url

def test_non_urls():
  _, is_url = normalise_yt_url("Never gonna give you up - rick astley")
  assert not is_url

  
