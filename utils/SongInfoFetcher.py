import re
from utils.Logger import *
from utils.Helper import Helper
import re
from pytube import YouTube, Search

helper = Helper()


async def videoSearch(songName, songUrl, video=False, res=480):
    try:
        if helper.isEmpty(songName):
            return None
        logInfo(f"Making call to fetch song details for : {songName} -> url : {songUrl}")

        # make call to fetch using the search query
        results = Search(songName if songUrl is None else songUrl).results
        song_infos = []
        for song in results[:1]:
            channelName = song.channel_id
            thumbnails = [] if song.thumbnail_url is None else [song.thumbnail_url]
            description = "" if song.description is None else song.description
            if video is True:
                filtered = (
                    song.streams.filter(progressive=True, file_extension="mp4")
                    .order_by("resolution")
                    .desc()
                )
            else:
                filtered = song.streams.filter(only_audio=True)

            if len(filtered) == 0:
                return None

            s_url, s_res = filtered[0].url, None
            for f in filtered:
                if video is True and f.resolution is not None:
                    resolution = re.findall("\d+", f.resolution)
                    if len(resolution) > 0 and int(res) <= int(resolution[0]):
                        s_url, s_res = [f.url, f.resolution]
                        break
                elif f.abr is not None:
                    resolution = re.findall("\d+", f.abr)
                    if len(resolution) > 0 and int(res) <= int(resolution[0]):
                        s_url, s_res = [f.url, f.abr]
                        break

            song_infos.append(
                {
                    "id": song.video_id,
                    "thumbnails": thumbnails,
                    "title": song.title,
                    "long_desc": description,
                    "channel": channelName,
                    "duration": song.length,
                    "views": song.views,
                    "link": s_url,
                    "resolution": s_res,
                    "is_video": video,
                }
            )
        return song_infos

    except Exception as ex:
        logException(f"Error while serching for youtube songs : {ex}")
        return None
