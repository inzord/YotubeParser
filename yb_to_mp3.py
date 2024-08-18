import re
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pytubefix import YouTube, Playlist
from params.params import Params
from cleaner.clean_folder import clean_folder
from scraping.scrap import get_browser, web_scraping

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class UrlToMp3:
    def __init__(self, urls: [str], path_out: str, max_threads: int):
        self.urls = urls
        self.path_out = path_out
        self.params = Params()
        self.max_threads = max_threads
        self.check = None

    def download_and_convert_video(self, link: str, only_audio: bool = True):
        yt = YouTube(link)
        stream = yt.streams.filter(only_audio=only_audio).first() if only_audio else yt.streams.first()
        out_file = stream.download(self.path_out)
        base, ext = os.path.splitext(out_file)
        new_file = base + self.params.MP3
        if not only_audio:
            video_clip = AudioFileClip(out_file)
            video_clip.write_audiofile(new_file)
            video_clip.close()
        else:
            os.rename(out_file, new_file)
        logging.info(f"Конвертация {link} в MP3 завершена")

    def process_video(self, link: str):
        logging.info(f"Начало обработки {link}")
        try:
            if link.find(self.params.PLAYLIST_CHECK) >= 0:
                if self.check == self.params.MIX_CHECK:
                    soup = get_browser(link)
                    new_data = web_scraping(soup)
                    for lin in new_data:
                        self.download_and_convert_video(lin, only_audio=False)
                else:
                    playlist = Playlist(link)
                    playlist._video_regex = re.compile(self.params.VIDEO_REGEX)
                    for video in playlist.videos:
                        self.download_and_convert_video(video.watch_url)
            else:
                self.download_and_convert_video(link)
        except Exception as exp:
            logging.error(f"Ошибка при обработке {link}: {exp}")
        finally:
            logging.info(f"Завершение обработки {link}")

    def process(self):
        for link in self.urls:
            if link.find(self.params.PLAYLIST_CHECK) >= 0:
                self.check = input(f'{self.params.PLAYLIST_CHECK}? or {self.params.MIX_CHECK}?: ')
                break

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.process_video, link) for link in self.urls]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exp:
                    logging.error(f"Ошибка при обработке ссылки: {exp}")

        clean_folder(self.path_out)


# "MIX"
# UrlToMp3(urls=["https://youtube.com/playlist?list=RDZrXwppk1fbs&playnext=1&si=y__BV-I1zWV5CMva",
#                "https://youtube.com/playlist?list=RDyi6NGtz53K4&playnext=1&si=8usYl6xZUAdCWGcY",
#                "https://youtube.com/playlist?list=RDqRsEjSBhtWo&playnext=1&si=AAw1pkniZVjvftAo"
#                ],
#          path_out=r'C:\Users\\OneDrive\Рабочий стол\music\test1', max_threads=5).process()

# "PLAYLIST"
# UrlToMp3(urls=["https://www.youtube.com/playlist?list=PLgULlLHTSGIQ9BeVZY37fJP50CYc3lkW2"],
#          path_out=r'C:\Users\\OneDrive\Рабочий стол\music\test', max_threads=5).process()

"VIDEO"
UrlToMp3(urls=["https://www.youtube.com/watch?v=bFoFN9Sbk2w", "https://www.youtube.com/watch?v=1ll3FvVk6BA"],
         path_out=r'C:\Users\\OneDrive\Рабочий стол\music\test2', max_threads=5).process()
