# DB2 - DogeBot2
## TL;DR
A simple Discord bot that play music in voice chat given any name or YouTube link.
## Starting Bot
* Make sure FFMPEG is installed.
* Create a .env in the root directory with: DISCORD_TOKEN = #your_discord_bot_token
* For Windows: Run bot_setup.bat to setup libraries. Run bot_start.bat to start the bot.
* For others: Activate the virtual environment. Install libraries in requirements.txt. Run main.py.
## Usage
* !play #name or link# : search for and play music in voice chat.
* !queue/!q : display current queue.
* !skip #location in queue# : without parameter: skip current song. with -1: skip last added song in queue.
  
