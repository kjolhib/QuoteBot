from __future__ import annotations

import discord
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from classes.quote_bot import QuoteBot

QuoteBotInteraction = discord.Interaction["QuoteBot"]
