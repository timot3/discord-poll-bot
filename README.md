# CS 196 Discord Poll Bot
This bot creates reactable polls for the CS 196 discord.

### Commands
You need administrator permissions to execute all of these commands. The bot will not respond if you do not have the 
proper permissions.

`poll set <channel id>`: Sets target channel where polls will be posted. **Run this command before creating a poll!**

`poll create <number of responses> <question text>`: Sends a poll to the target channel and reacts to the message with 
the set number of responses. 
* When a user responds to the message, the bot removes the reaction after storing the result.
* If a user changes their answer, the new answer is recorded instead of the original.
* When a new poll is created, the bot doesn't save the old answers! Be sure to run `poll results` to save poll answers.

`poll results`: Saves the poll results to a `.csv` file and sends them to the same channel the command was invoked.
