import re
from utils.Logger import *
from pytube import Search, YouTube


def parseResult(song, video=False, res=480):
    try:
        channelName = song.channel_id
        thumbnails = [] if song.thumbnail_url is None else [song.thumbnail_url]
        description = "" if song.description is None else song.description
        if video is True:
            filtered = (
                song.streams.filter(progressive=True, file_extension="mp4")
                .order_by("resolution")
                .desc()
            )
            audio_filtered = song.streams.filter(only_audio=True).order_by("abr").desc()
        else:
            filtered = song.streams.filter(only_audio=True).order_by("abr").desc()

        if len(filtered) == 0:
            return None

        s_url, s_res, audio = (
            filtered[0].url,
            None,
            (audio_filtered[0].url if video is True else None),
        )
        for f in filtered:
            if video is True and f.resolution is not None:
                resolution = re.findall("\d+", f.resolution)
                if len(resolution) > 0 and int(resolution[0]) <= int(res):
                    s_url, s_res, audio = [f.url, f.resolution, audio]
                    break
            elif f.abr is not None:
                resolution = re.findall("\d+", f.abr)
                if len(resolution) > 0 and int(resolution[0]) <= int(res):
                    s_url, s_res, audio = [f.url, f.abr, None]
                    break

        return {
            "id": song.video_id,
            "thumbnails": thumbnails,
            "title": song.title,
            "long_desc": "",
            "channel": channelName,
            "duration": int(song.length) if song.length else None,
            "views": song.views,
            "link": s_url,
            "audio_link": audio,
            "resolution": s_res,
            "is_video": video,
        }

    except Exception as ex:
        raise Exception(ex)


async def VideoSearch(songName, songUrl, video=False, res=480):
    try:
        if not songName:
            return None
        logInfo(
            f"Making call to fetch song details for : {songName} -> url : {songUrl}"
        )
        # make call to fetch using the search query
        if not songUrl:
            results = Search(songName).results
        else:
            results = [YouTube(songUrl)]
        song_infos = []
        for song in results[:1]:
            song_infos.append(parseResult(song, video, res))
        return song_infos
    except Exception as ex:
        logException(f"Error while serching for youtube songs : {ex}")
        raise Exception(ex)


async def VideoFetchFromId(songId, video=False, res=480):
    try:
        if not songId:
            return None
        logInfo(f"Making call to fetch song details for id : {songId}")
        # make call to fetch using the search query
        resp = YouTube(f"http://youtube.com/watch?v={songId}")
        if res and len(res) > 0:
            nums = re.findall("\d+.\d+|\d+", res)
            res = nums[0] if nums else 480
        return parseResult(resp, video, res)
    except Exception as ex:
        logException(f"Error in VideoFetchFromId : {ex}")
        raise Exception(ex)
