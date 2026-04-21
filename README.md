# What it is
QuoteBot is a discord bot that contains commands related to DnD, randomness, and other miscellaneous commands. It was created for private use for mostly DnD purposes for my friends.
# Limitations
Currently not all commands are open. Since it was created for private use, some commands are used and created for specific scenarios.

I also don't plan to make the bot publicly available (though haven't really looked into it).
# Commands
<details>
<summary>

## DnD

</summary>

  <details>
  <summary>
    
  #### /start
    
  </summary>
  
  Starts a DnD session. Grants access to the following commands:
  - [/new_dice](#new_dice)
  - [/remove_dice] (#remove_dice)
  - [/instance_dice](#instance_dice)
  </details>

  <details>
  <summary>
  
  #### /end

  </summary>
  Ends a DnD session.

  </details>

  <details>
  <summary>
    
  #### /new_dice

  </summary>
  
  Creates a new weighted die, with a specified number of `faces`, and of a specific `scenario`.
  
  All instances are destroyed upon bot going offline.
  </details>

  <details>
  <summary>
  
  ### /remove_dice
  
  </summary>
  
  Removes an existing die, specified by `scenario`.

  </details>

  <details>
  <summary>

  #### /instance_dice

  </summary>
  
  Rolls the weighted instance dice with the scenario `scenario`. Instance dices are created with [/new_dice](#new_dice).
  
  
  The dice rolls will be weighted to not favour the previous. Similar to how Markov Chains weights work.
  </details>

  <details>
  <summary>
    
  #### /list_dice
  </summary>
  Lists the instance die currently active.

  </details>

  <details>
  <summary>
    
  #### /weather
  </summary> 
  
  This is currently not open to all.
  
  Generates a random weighted weather from a JSON file. The JSON file contains a key-value pair of the weather string - how often it was rolled. The more each weather is rolled, the less likely it will be rolled next.
  
  </details>

  <details>
  <summary>
    
  #### /weather_stats
  </summary>
  
  This is currently not open to all.
  
  Returns an embed, structured like the JSON file in more readable format.

  </details>

  <details>
  <summary>
    
  #### /add_weather
  </summary>
  
  This is currently not open to all.
  
  Modifies the weather JSON file by adding a new weather of a specified `scenario`.

  </details>

  <details>
  <summary>
    
  #### /remove_weather
  </summary>
  
  This is currently not open to all.
  
  Modifies the weather JSON file by removing an existing weather of a specified `scenario`.

  </details>

  <details>
  <summary>
    
  #### /modify_weather
  </summary>
  
  This is currently not open to all.
  
  Modifies a specific `scenario`'s key-value pair to a `new_count`. Useful to backtrack if any extra rolls were made.

  </details>

  <details>
  <summary>
  
  #### /get_raw_weather_json
  </summary>
  
  This is currently not open to all.
  
  Outputs the raw JSON file.

  </details>
</details>

<details>
<summary>

## Voice

</summary>
  
  NOTE: ALL COMMANDS, EXCEPT [JOIN](#join) AND [LEAVE](#leave) ARE NOT CURRENTLY OPEN FOR USE. THIS MAY OR MAY NOT CHANGE IN THE FUTURE.

  <details>
  <summary>
  
  #### /join
  </summary>
  
  Joins VC. If already in VC in guild, changes VC to sender's.
  
  </details>

  <details>
  <summary>
  
  #### /leave
  </summary>
  
  Leaves the VC. If not in VC, sends appropriate message.

  </details>

  <details>
  <summary>
    
  #### /play
  </summary>
  
  Given a string `s` that can be either a link or query, plays a song. Timeout is 20 seconds.
  
  If no valid video found, sends an appropriate message. 
  
  Note (as of 31/3/2026), with links, youtube links that aren't "standard" (`www.youtube.com.watch?v=...`) will cause the bot to not find that video. I believe it has something to do with youtube having multiple formats that redirect to the "standard" link, though I have not looked deeply into it.

  </details>

  <details>
  <summary>
    
  #### /skip
  </summary>
  
  Skips the current song playing.
  Sends appropriate messages if none playing or not in VC.

  </details>

  <details>
  <summary>
    
  #### /queue
  </summary>
  
  Lists the queue and currently playing song.

  </details>

  <details>
  <summary>
    
  #### /pause

  </summary>
  Pauses the currently playing song.

  </details>

  <details>
  <summary>
    
  #### /resume

  </summary>
  
  Resumes the currently paused song.

  </details>

  <details>
  <summary>
    
  #### /repeat

  </summary>
  
  Repeats the current song.
  </details>

</details>

<details>
<summary>

## Miscellaneous

</summary>

  <details>
  <summary>
    
  #### /random_msg
  </summary>
  
  Returns a random message sent by `user` specified by sender.
  Has optional arguments:
  - `limit`: Limits the number of previous messages the bot will look through. Default is 200. Too large of a number, and the operation may time out.
  - `min_count`: If the specified user sent less than `min_count`, then the command will return a message that the user sent too few messages.
  
  </details>

  <details>
  <summary>
    
  #### /repeat_after_me
  </summary>  
  
  Repeats whatever the user sent. Was a test originally, may remove later.
  
  </details>

  <details>
  <summary>
    
  #### /dice
  </summary>
    
  Rolls a dice, with the number of `faces` specified.
  Has optional arguments:
  - `addon`: The result of the dice roll will be added onto `addon`. `addon` is then returned as the final result.

  </details>

  <details>
  <summary>
    
  #### /timezone

  </summary>
  
  Uses IANA format to return the time in a specified `target_city` and `origin_city`. Requires `origin_country`, `time`, `target_country`, and `date_str`.
  
  Was used as a test. May remove in the future.

  </details>
</details>
