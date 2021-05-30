# Telegram VCPlayer Bot
Play any song directly into your group voice chat.

Official Bot : [VCPlayerBot](https://telegram.me/vcplayerbot)   |   Discussion Group : [VoiceChat Music Player Support](https://telegram.me/voicechatsupport)

<p align="center">
  <img width="200" height="200" src="https://i.postimg.cc/QdH3XrxV/Screenshot-2021-05-05-203005-removebg-preview.png">
</p>

[Checkout AutoForwarder Bot](https://sktechhub.com/auto-forward)


# Requirements
1. Telegram Api Id and Hash
2. Python 3.6+
3. ffmpeg
4. Mongo DB

# Steps To Setup
1. Generate your telegram session string (using pyrogram).
2. Rename `.env copy` to `.env` and fill all the required fields in there.
3. In Mongo DB a database named `sktechhub` will be created with the collections `tgcalls_chats` , `tgcalls_playbacks` , `tgcalls_users` ( if not present then create them manually). 

# Steps to Run
1. After the setup is done.
2. Install ffmpeg : `sudo apt-get install ffmpeg`
3. Install the requirements : `pip3 install -U -r requirements.txt`
4. Run the service : `python3 main.py -env prod -service call`

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
