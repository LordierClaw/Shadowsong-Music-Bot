import re
from youtube_dl import YoutubeDL
from .ServerQueue import Video as Video

class Playlist:
    def __init__(self, title:str, count:int, items=[]):
        self.title = title
        self.count = count
        self.items = items

class YoutubeParser():
    def get_video_id(url: str):
        VIDEO_ID_REGEX = r"^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
        getRegex = re.compile(VIDEO_ID_REGEX)
        try:
            video_id = (getRegex.search(url)).group(7)
        except:
            video_id = None
        return video_id

    def get_playlist_id(url: str):
        PLAYLIST_ID_REGEX = r"[&?]list=([^&]+)"
        getRegex = re.compile(PLAYLIST_ID_REGEX)
        try:
            playlist_id = (getRegex.search(url)).group(1)
        except:
            playlist_id = None
        return playlist_id

class YoutubeExtractor():
    def search_yt(query:str):
        ydl_opts = {
            'extract_flat': True,
            'noplaylist': True,
            'quiet': False,
            'source_address': '0.0.0.0'
        }
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            id = result["id"]
            title = result["title"]
            length = result["duration"]
        return Video(id, title, length)

    def get_audio(id:str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '140',
            }],
            'outtmpl': '%(title)s.%(etx)s',
            'quiet': False,
            'source_address': '0.0.0.0'
        }
        url = f"https://www.youtube.com/watch?v={id}"
        with YoutubeDL(ydl_opts) as ydl:
            ydl._ies = [ydl.get_info_extractor('Youtube')] #get exact extractor, no need for query
            result = ydl.extract_info(url, download=False)
            audio_url = result["formats"][0]["url"]
        return audio_url

    def get_video(url:str):
        ydl_opts = {
            'extract_flat': True,
            'quiet': False,
            'source_address': '0.0.0.0' # bind to ipv4
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl._ies = [ydl.get_info_extractor('Youtube')] #get exact extractor, no need for query
            result = ydl.extract_info(url, download=False)
            id = result["id"]
            title = result["title"]
            length = result["duration"]
        return Video(id, title, length)

    def get_playlist(url:str):
        all_items = []

        ydl_opts = {
            'extract_flat': 'in_playlist',
            'quiet': False,
            'source_address': '0.0.0.0'
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl._ies = [ydl.get_info_extractor('YoutubeTab')] #get exact extractor, no need for query
            playlist_info = ydl.extract_info(url, download=False)
            title = playlist_info["title"]
            count = len(playlist_info["entries"])
            for item in playlist_info["entries"]:
                vid = Video(item["id"], item["title"], item["duration"])
                all_items.append(vid)
        return Playlist(title, count, all_items)
