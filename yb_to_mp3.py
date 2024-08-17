import re
import threading
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
        self.check = None
        self.urls = urls
        self.path_out = path_out
        self.mp3 = Params().MP3
        self.mp4 = Params().MP4
        self.video_regex = Params().VIDEO_REGEX
        self.youtube_stream_audio = Params().YOUTUBE_STREAM_AUDIO
        self.playlist_check = Params().PLAYLIST_CHECK
        self.mix_check = Params().MIX_CHECK
        self.max_threads = max_threads

    def video_to_mp3(self, links: str):
        logging.info(f"Начало конвертации видео {links} в MP3")
        yt = YouTube(links)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(self.path_out)
        base, ext = os.path.splitext(out_file)
        new_file = base + self.mp3
        os.rename(out_file, new_file)
        logging.info(f"Завершение конвертации видео {links} в MP3")

    def mix_playlist_to_mp3(self, links: str):
        logging.info(f"Начало конвертации микса {links} в MP3")
        yt = YouTube(links)
        video = yt.streams.first()
        out_file = video.download(self.path_out)
        new_file = out_file.replace(self.mp4, self.mp3)
        video_clip = AudioFileClip(out_file)
        video_clip.write_audiofile(new_file)
        logging.info(f"Завершение конвертации микса {links} в MP3")

    def playlist_to_mp3(self, links: str):
        logging.info(f"Начало конвертации плейлиста {links} в MP3")
        playlist = Playlist(links)
        playlist._video_regex = re.compile(self.video_regex)
        for video in playlist.videos:
            out_file = video.streams.get_by_itag(self.youtube_stream_audio).download(self.path_out)
            new_file = out_file.replace(self.mp4, self.mp3)
            video_clip = AudioFileClip(out_file)
            video_clip.write_audiofile(new_file)
        logging.info(f"Завершение конвертации плейлиста {links} в MP3")

    def process_video(self, link: str):
        logging.info(f"Начало обработки {link} в потоке {threading.current_thread().name}")
        try:
            if link.find(self.playlist_check) >= 0:
                if self.check == self.mix_check:
                    new_data = []
                    soup = get_browser(link)
                    new_data.append(web_scraping(soup))
                    logging.info(f"Скрапинг данных для {link} завершен")
                    for link in new_data:
                        for lin in link:
                            self.mix_playlist_to_mp3(lin)
                else:
                    self.playlist_to_mp3(link)
            else:
                self.video_to_mp3(link)
        except Exception as ex:
            logging.error(f"Ошибка при обработке {link}: {ex}")
        finally:
            logging.info(f"Завершение обработки {link} в потоке {threading.current_thread().name}")

    def process(self):
        all_links = []
        for link in self.urls:
            if link.find(self.playlist_check) >= 0:
                self.check = input(f'{self.playlist_check}? or {self.mix_check}?: ')
                break

        for link in self.urls:
            if link.find(self.playlist_check) >= 0:
                if self.check == self.mix_check:
                    new_data = []
                    soup = get_browser(link)
                    new_data.append(web_scraping(soup))
                    logging.info(f"Скрапинг данных для {link} завершен")
                    for sub_link in new_data:
                        all_links.extend(sub_link)
                else:
                    playlist = Playlist(link)
                    playlist._video_regex = re.compile(self.video_regex)
                    all_links.extend([video.watch_url for video in playlist.videos])
            else:
                all_links.append(link)

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.process_video, link) for link in all_links]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as ex:
                    logging.error(f"Ошибка при обработке ссылки: {ex}")

        clean_folder(self.path_out)


# "MIX"
# UrlToMp3(urls=["https://youtube.com/playlist?list=RDZrXwppk1fbs&playnext=1&si=y__BV-I1zWV5CMva",
#                "https://youtube.com/playlist?list=RDyi6NGtz53K4&playnext=1&si=8usYl6xZUAdCWGcY",
#                "https://youtube.com/playlist?list=RDqRsEjSBhtWo&playnext=1&si=AAw1pkniZVjvftAo"
#                ],
#          path_out=r'C:\Users\dfrty\OneDrive\Рабочий стол\music\test1', max_threads=5).process()

# "PLAYLIST"
# UrlToMp3(urls=["https://www.youtube.com/playlist?list=PLgULlLHTSGIQ9BeVZY37fJP50CYc3lkW2"],
#          path_out=r'C:\Users\dfrty\OneDrive\Рабочий стол\music\test', max_threads=5).process()

"VIDEO"
UrlToMp3(urls=["https://www.youtube.com/watch?v=bFoFN9Sbk2w", "https://www.youtube.com/watch?v=1ll3FvVk6BA"],
         path_out=r'C:\Users\dfrty\OneDrive\Рабочий стол\music\test2', max_threads=5).process()
