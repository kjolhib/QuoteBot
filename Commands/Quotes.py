import random
from Helpers.Timezone_helper import format_AEST
from Helpers.Utility_helpers import safe_send
from Helpers.Quote_helpers import *
from ErrorHandler import ErrorHandler as eh

"""
Commands
"""
async def run_repeat(interaction, string):
  try:
    await safe_send(interaction, f'{string}')
  except Exception as e:
    await safe_send(interaction, f"[ERROR]: repeat_after_me: error sending message: {e}")
    err = eh.Error(e, "/repeat_after_me")
    eh.report_error(err)

async def rand(interaction, user, limit, min_count):
  """
  Sends a random single text user sent in this server. Quotes the user.
  :params user: the user to find a quote of
  """
  try:
    # Don't try to quote itself
    if user.id == interaction.client.user.id:
      return await safe_send(interaction, "Stop trying to quote me, I'm above your whimsical interactions!")

    if not limit:
      limit = 200
    if not min_count:
      min_count = 0
    msg = await get_random_message(interaction, user, limit, min_count)
    
    if not msg:
      print(f"No messages sent: {limit}")
      return await safe_send(interaction, f"This user has not sent any messages in the last {limit} messages, disappointing...")
    elif msg == 401:
      return await safe_send(interaction, f"{user.name} has sent less than 5 messages recently!")

    timestamp = format_AEST(msg.created_at, "%Y-%m-%d %H:%M:%S")
    return await safe_send(interaction, '"' + msg.content + '"' + " - " + user.name + " (" + timestamp + ")")
  except Exception as e:
    print(f"[ERROR]: random_msg: error initialising: {e}")
    await safe_send(interaction, f"An error occurred. Try again later or check logs.")
    err = eh.Error(e, "/random_msg")
    eh.report_error(err)
