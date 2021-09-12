import re
from utils.Logger import *
from pytube import Search


async def VideoSearch(songName, songUrl, video=False, res=480):
    try:
        if not songName:
            return None
        logInfo(
            f"Making call to fetch song details for : {songName} -> url : {songUrl}"
        )

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
                audio_filtered = (
                    song.streams.filter(only_audio=True).order_by("abr").desc()
                )
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

            song_infos.append(
                {
                    "id": song.video_id,
                    "thumbnails": thumbnails,
                    "title": song.title,
                    "long_desc": description,
                    "channel": channelName,
                    "duration": f"{song.length} sec",
                    "views": song.views,
                    "link": s_url,
                    "audio_link": audio,
                    "resolution": s_res,
                    "is_video": video,
                }
            )
        return song_infos

    except Exception as ex:
        logException(f"Error while serching for youtube songs : {ex}")
        return None
