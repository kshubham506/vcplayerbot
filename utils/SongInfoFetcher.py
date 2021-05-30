import re
from utils.Logger import *
from utils.Helper import Helper
from youtube_search import YoutubeSearch
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
        results = YoutubeSearch(
            (songName if song_url is None else song_url), max_results=maxresults).to_dict()
        return results

    except Exception as ex:
        logException(f"Error while serching for youtube songs : {ex}")
        return None
