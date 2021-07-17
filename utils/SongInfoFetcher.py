import re
from utils.Logger import *
from utils.Helper import Helper
from youtubesearchpython import VideosSearch
import re

helper = Helper()


async def YouTubeSearch(songName, maxresults=1):
    try:

        if songName in ["", None]:
            return None
        urls = helper.getUrls(songName)
        song_url = None
        logInfo(f"Making call to fetch song details for : {songName}")
        if urls is not None and len(urls) > 0:
            if len(urls) > 1:
                return None
            elif re.search("youtube\.|youtu\.be|youtube-nocookie\.", urls[0]):
                song_url = urls[0]
            else:
                return None

        # make call to fetch using the search query
        results = VideosSearch(
            (songName if song_url is None else song_url), limit=maxresults).result()
        song_infos = []
        for song in results['result']:
            channelName = song.get("channel")['name'] if song.get(
                "channel") is not None else ""
            thumbnails = [] if song.get("thumbnails") is None or len(
                song.get("thumbnails")) == 0 else [t['url'] for t in song.get("thumbnails")]
            description = "" if song.get("descriptionSnippet") is None or len(song.get("descriptionSnippet")) == 0 else song.get(
                "descriptionSnippet")[0]['text']
            song_infos.append({
                'id': song['id'], 'thumbnails': thumbnails,
                'title': song['title'], 'long_desc': description, 'channel': channelName, 'duration': song['duration'],
                'views': song['viewCount']['text'], 'publish_time': song['publishedTime'], 'link': song['link']
            })
        return song_infos

    except Exception as ex:
        logException(f"Error while serching for youtube songs : {ex}")
        return None
