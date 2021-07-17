# Telegram VCPlayer Bot
Play any song directly into your group voice chat.

Official Bot : [VCPlayerBot](https://telegram.me/vcplayerbot)   |   Discussion Group : [VoiceChat Music Player Support](https://telegram.me/voicechatsupport)

<p align="center">
  <img width="200" height="200" src="https://i.postimg.cc/QdH3XrxV/Screenshot-2021-05-05-203005-removebg-preview.png">
</p>

[Checkout AutoForwarder Bot](https://sktechhub.com/auto-forward)


# Requirements
1. Telegram Api Id and Hash [ Get it from my.telegram.org ]
2. A Telegram Bot Token. Get it from @botfather.
3. Python 3.6+
4. ffmpeg [ [How to Install ? ](https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-18-04/) ]
5. [ Optional ] Mongo DB [ Create free account from mongo website and get your connection string. ] 

# Deploying To Heroku
1. Get your telegram API ID and API HASH from my.telegram.org and the BOT TOKEN from @botfather.
2. Generate your telegram session string using the `Run on Repl` button below (Click on run after opening the url below) or use the `generateSession.py` file.

- [![Run on Repl.it](https://repl.it/badge/github/kshubham506/vcplayerbot)](https://replit.com/@kshubham506/GenerateSession?lite=1&outputonly=1)


3. Clcik on the `Deploy to Heroku` button below. Fill in the required fields on the website that opens.

- [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

4. Add the bot to your group and send the [commands](https://github.com/kshubham506/vcplayerbot#features) to start using the VCPlayer Bot :)


# Steps To Setup
1. Install pyrogram for generatong session string : `pip3 install -U pyrogram`
2. Generate your telegram session string. Run `python3 generateSession.py`
3. Rename `.env copy` to `.env` and fill all the required/mandatory fields in there.
4. [ Optional ] In Mongo DB a database named `sktechhub` will be created with the collections `tgcalls_chats` , `tgcalls_playbacks` , `tgcalls_users` ( if not present then create them manually). 

# Steps to Run
1. After the setup is done.
2. Install ffmpeg : `sudo apt-get install ffmpeg`
3. Install the requirements : `pip3 install -U -r requirements.txt`
4. Run the service by : 
  - Run `python3 main.py --help` for available settings.  
  - Or Run `python3 main.py -env prod` to use default settings

# Features
Command | Description
------------ | -------------
/start , /help | Lists the available commands.
/play song_name | Starts the song in the voice chat.
/skip | Skips the current song.
/stop | Stops the playback.
/loop off , /loop [2-5] | Loops the song to x times.
/info | Shows the info of the playback in the chat.
/refreshadmins | Refreshes the admin list in the chat.
/auth | Adds the user mentioned in the reply to bot admin list.
/unauth | Removes the user mentioned in the reply from bot admin list.
/listadmins | Lists all the bot admins.
/adminmode [on,off] | Turn on/off the admin mode.

<p align="center">
  <img width="500" height="300" src="https://i.postimg.cc/qRtC4bD2/photo-2021-05-28-00-15-11.jpg">
</p>

# Developer
[Shubham Kumar](https://github.com/kshubham506)

For any issues/questions please contact [here](https://telegram.me/voicechatsupport)

Pull Requests are more than welcome.


 ### [A SkTechHub Product](https://sktechhub.com)
