import re
import os, googleapiclient.discovery

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

class YoutubeAPI():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey = os.getenv('YOUTUBE_API_KEY'))

    def get_video_title(self, video_id: str): #youtube_api 
        request = self.youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        video_title = response["items"][0]["snippet"]["title"]
        return str(video_title)
    
    def get_playlist_info(self, playlist_id: str, type: str): #youtube_api
        request = self.youtube.playlists().list(
            part="snippet,contentDetails",
            id=playlist_id
        )
        response = request.execute()
        if type == "title":
            result = response["items"][0]["snippet"]["title"]
        elif type == "count":
            result = response["items"][0]["contentDetails"]["itemCount"]
        elif type == "all":
            result = response
        return result
        