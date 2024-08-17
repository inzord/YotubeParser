import os

from dotenv import load_dotenv

load_dotenv()


class Params:

    def __init__(self):
        self.YOUTUBE_STREAM_AUDIO = os.getenv("youtube_stream_audio")
        self.Y_B = os.getenv("y_b")
        self.MP3 = os.getenv("mp3")
        self.MP4 = os.getenv("mp4")
        self.PLAYLIST_CHECK = os.getenv("playlist_check")
        self.MIX_CHECK = os.getenv("mix_check")
        self.VIDEO_REGEX = os.getenv("video_regex")
        self.USER_AGENT = os.getenv("user_agent")
