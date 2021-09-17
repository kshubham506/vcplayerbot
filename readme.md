# Telegram VCPlayer Bot
Play any media(song, video, live, remote) directly into your group voice chat.

Official Bot : [VCPlayerBot](https://telegram.me/vcplayerbot)   |   Discussion Group : [VoiceChat Music Player Support](https://telegram.me/voicechatsupport)

<p align="center">
  <img width="200" height="200" src="https://i.postimg.cc/QdH3XrxV/Screenshot-2021-05-05-203005-removebg-preview.png">
</p>

[Checkout AutoForwarder Bot](https://sktechhub.com/auto-forward) | [Try Code Compile Bot](https://t.me/codecompilebot)


# Requirements
1. Telegram Api Id and Hash [ Get it from http://my.telegram.org ]
2. A Telegram Bot Token. Get it from [@botfather](https://t.me/botfather) 
3. Python 3.6+
4. [ Optional, only use if you are an advanced user ] Mongo DB [ Create free account from mongo website and get your connection string. ] 

# Deploying To Heroku
1. Get your telegram API ID and API HASH from my.telegram.org and the BOT TOKEN from [@botfather](https://t.me/botfather)
2. Generate your telegram session string using the `Run on Repl` button below (Click on run after opening the url below) or use the `generateSession.py` file or read the steps [mentioned here](get_session_string.md).

- [![Run on Repl.it](https://repl.it/badge/github/kshubham506/vcplayerbot)](https://replit.com/@kshubham506/GenerateSession?lite=1&outputonly=1)


3. Click on the `Deploy to Heroku` button below. Fill in the required fields on the website that opens.

- [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

4. Add the bot to your group and send the [commands](https://github.com/kshubham506/vcplayerbot#features) to start using the VCPlayer Bot :)


# Steps To Setup on VPC or Locally
1. Read the steps [mentioned here](get_session_string.md) to get your session string.
2. Rename `.env copy` to `.env` and fill all the values there. You can leave the `MONGO_URL` line as it is (only fill if you know what you are doing)


# Steps to Run
1. After the setup is done.
2. Install the requirements : `pip3 install -U -r requirements.txt`
3. Run the service by : 
  - Run `python3 main.py -env prod` 
  
  - (make sure `-env prod` flag is provided, if not rename `.env` file to `.env.copy`)

# Environmental Variables

Starting from command line:
- python3 main.py -env `prod|local`

Available env variables
- `Mandataory` **API_ID** :  get it from my.telegram.org
- `Mandataory` **API_HASH** : get it from my.telegram.org
- `Mandataory` **BOT_TOKEN** : bot token of your music bot, get it from @botfather
- `Mandataory` **USERBOT_SESSION** : user bot pyrogram session string, read the steps [mentioned here](get_session_string.md) to get your session string.
- `Optional` **MONGO_URL** : connection url for mongo databse. needed if you wnat to run the service in single mode

- Many other optional variables, check [Config.py](utils/Config.py) file for details.

# Features
Streams directly from url, Playlist support

Command | Description
------------ | -------------
/start , /help | Lists the available commands.
/play song_name/song_url -res[num] | Starts the song in the voice chat, num specifies the audio resolution. eg. `/play coldplay -res256` → plays coldplay song in 256 bit rate
/play song_name/song_url -video -res[num] | Starts the video in the voice chat, num specifies the video resolution. eg. `/play coldplay -res2480` → plays coldplay video in 480p
/skip | Skip the current media playback.
/stop | Stops the playback.



<p align="center">
  <img width="500" height="300" src="https://i.postimg.cc/qRtC4bD2/photo-2021-05-28-00-15-11.jpg">
</p>

# Developer
[Shubham Kumar](https://github.com/kshubham506)

For any issues/questions please contact [here](https://telegram.me/voicechatsupport)

Pull Requests are more than welcome.


 ### [A SkTechHub Product](https://sktechhub.com)
