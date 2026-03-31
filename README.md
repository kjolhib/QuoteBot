# What it is
QuoteBot is a discord bot that contains commands related to DnD, randomness, and other miscellaneous commands. It was created for private use for mostly DnD purposes for my friends.
# Limitations
Currently not all commands are open. Since it was created for private use, some commands are used and created for specific scenarios that my friends may require.
# Commands
<details>
  <summary>DnD</summary>
  
  ### /start
  Starts a DnD session. Grants access to the following commands:
  - [/new_dice](#new_dice)
  - [/instance_dice](#instance_dice)

  ### /end
  Ends a DnD session.
  
  ### /new_dice
  Creates a new weighted dice, with a specified number of `faces`, and of a specific `scenario`.
  
  All instances are destroyed upon bot going offline.
  
  ### /instance_dice
  Rolls the weighted instance dice with the scenario `scenario`. Instance dices are created with (/new_dice)[#new_dice].
  
  The dice rolls will be weighted to average out as much as possible, that is, the lesser a specific number is rolled, the higher probability it will be rolled next.
  
  ### /list_dice
  Lists the instance die currently active.

  ### /weather
  This is currently not open to all.
  
  Generates a random weighted weather from a JSON file. The JSON file contains a key-value pair of the weather string - how often it was rolled. The more each weather is rolled, the less likely it will be rolled next.

  ### /weather_stats
  This is currently not open to all.
  
  Returns an embed, structured like the JSON file in more readable format.
  
  ### /add_weather
  This is currently not open to all.
  
  Modifies the weather JSON file by adding a new weather of a specified `scenario`.
  
  ### /remove_weather
  This is currently not open to all.
  
  Modifies the weather JSON file by removing an existing weather of a specified `scenario`.
  
  ### /modify_weather
  This is currently not open to all.
  
  Modifies a specific `scenario`'s key-value pair to a `new_count`. Useful to backtrack if any extra rolls were made.
  
  ### /get_raw_weather_json
  This is currently not open to all.
  
  Outputs the raw JSON file.
</details>

<details>
<summary>Voice</summary>
  
  NOTE: ALL COMMANDS, EXCEPT [JOIN](#join) AND [LEAVE](#leave) ARE NOT CURRENTLY OPEN FOR USE. THIS MAY OR MAY NOT CHANGE IN THE FUTURE.
  
  ### /join
  Joins VC. If already in VC in guild, changes VC to sender's.
  
  ### /leave
  Leaves the VC. If not in VC, sends appropriate message.
  
  ### /play
  Given a link or query, plays a song. Timeout is 20 seconds.
  
  If no valid video found, sends an appropriate message. 
  
  Note (as of 31/3/2026), with links, youtube links that aren't "standard" (`www.youtube.com.watch?v=...`) will cause the bot to not find that video. I believe it has something to do with youtube having multiple formats that redirect to the "standard" link, though I have not looked deeply into it.
  
  ### /skip
  Skips the current song playing.
  Sends appropriate messages if none playing or not in VC.
  
  ### /queue
  Lists the queue and currently playing song.
  
  ### /pause
  Pauses the currently playing song.
  
  ### /resume
  Resumes the currently paused song.
  
  ### /repeat
  Repeats the current song.

</details>

<details>
<summary>Miscellaneous</summary>

  ### /random_msg
  Returns a random message sent by `user` specified by sender.
  Has optional arguments:
  - `limit`: Limits the number of previous messages the bot will look through. Default is 200. Too large of a number, and the operation may time out.
  - `min_count`: If the specified user sent less than `min_count`, then the command will return a message that the user sent too few messages.
  
  ### /repeat_after_me
  Repeats whatever the user sent. Was a test originally, may remove later.
  
  ### /dice
  Rolls a dice, with the number of `faces` specified.
  Has optional arguments:
  - `addon`: The result of the dice roll will be added onto `addon`. `addon` is then returned as the final result.
  
  ### /timezone
  Uses IANA format to return the time in a specified `target_city` and `origin_city`. Requires `origin_country`, `time`, `target_country`, and `date_str`.
  
  Was used as a test. May remove in the future.

</details>
