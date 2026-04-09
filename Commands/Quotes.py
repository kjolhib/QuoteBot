import random
from Helpers.Timezone_helper import format_AEST
from Helpers.Utility_helpers import safe_send
from Helpers.Quote_helpers import *
from ErrorHandler import ErrorHandler as eh

async def run_repeat(interaction, string):
  """
  Repeats the string specified by the user.
  Used to debug and check that the bot actually connected and responded to the user. 
  Essentially useless command.
  """
  try:
    await safe_send(interaction, f'{string}')
  except Exception as e:
    await safe_send(interaction, f"[ERROR]: repeat_after_me: error sending message: {e}")
    err = eh.Error(e, "/repeat_after_me")
    eh.report_error(err)

async def rand(interaction, user, limit, min_count):
  """
  Sends a random single text user sent in this server.
  Quotes the user.
  Params:
    - user: the user to quote. The bot will get a random message from this user
    - limit: the bot will go through the last n messages defined by this variable. ie. limit=200, the bot will check the last 200 messages sent in this channel. Primarily here for timeout purposes. Defaulted to 200
    - min_count: the minimum number of messages sent by the user where the bot will not output a random message. ie. min_count = 2, if the user has sent < than 2, then the bot will not try to quote. This is mostly to reduce the possibility of the same messages being quoted over and over.
  
  Returns:
    - random message chosen
    - if min_count specified and num messages < min_count, an appropriate message
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
