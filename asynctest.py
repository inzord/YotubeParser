import re
import asyncio
import aiohttp
import os
import time
from concurrent.futures import ThreadPoolExecutor

from moviepy.audio.io.AudioFileClip import AudioFileClip
from pytubefix import YouTube, Playlist

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from params.params import Params
from cleaner.clean_folder import clean_folder


async def web_scraping(soup):
    list_urls = []
    for org in soup.findAll('a', id='wc-endpoint'):
        name = org.get('href')
        link = "".join([Params().Y_B, name])
        list_urls.append(link)
    return list_urls


async def get_browser(links):
    o = Options()
    o.add_argument(Params().USER_AGENT)
    o.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=o)
    browser.get(links)

    await asyncio.sleep(10)

    soup = BeautifulSoup(browser.page_source, 'lxml')
    browser.close()
    return soup


class UrlToMp3:
    def __init__(self, urls: [str], path_out: str):
        self.check = None
        self.urls = urls
        self.path_out = path_out
        self.mp3 = Params().MP3
        self.mp4 = Params().MP4
        self.video_regex = Params().VIDEO_REGEX
        self.youtube_stream_audio = Params().YOUTUBE_STREAM_AUDIO
        self.playlist_check = Params().PLAYLIST_CHECK
        self.mix_check = Params().MIX_CHECK

    async def video_to_mp3(self, links: str):
        yt = YouTube(links)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(self.path_out)

        base, ext = os.path.splitext(out_file)
        new_file = base + self.mp3
        os.rename(out_file, new_file)

    async def mix_playlist_to_mp3(self, links: str):
        yt = YouTube(links)
        video = yt.streams.first()
        out_file = video.download(self.path_out)

        new_file = out_file.replace(self.mp4, self.mp3)
        video_clip = AudioFileClip(out_file)
        video_clip.write_audiofile(new_file)

    async def playlist_to_mp3(self, links: str):
        playlist = Playlist(links)
        playlist._video_regex = re.compile(self.video_regex)

        for video in playlist.videos:
            out_file = video.streams.get_by_itag(self.youtube_stream_audio).download(self.path_out)
            new_file = out_file.replace(self.mp4, self.mp3)
            video_clip = AudioFileClip(out_file)

            video_clip.write_audiofile(new_file)

    async def process_video(self, link):
        try:
            if link.find(self.playlist_check) >= 0:
                if self.check == self.mix_check:
                    new_data = []
                    soup = await get_browser(link)
                    new_data.append(await web_scraping(soup))
                    for link in new_data:
                        for lin in link:
                            await self.mix_playlist_to_mp3(lin)
                else:
                    await self.playlist_to_mp3(link)
            else:
                await self.video_to_mp3(link)
        except Exception as ex:
            print(ex)
        finally:
            await asyncio.sleep(3)
            clean_folder(self.path_out)

    async def process(self):
        for link in self.urls:
            if link.find(self.playlist_check) >= 0:
                self.check = input(f'{self.playlist_check}? or {self.mix_check}?: ')
                break

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            tasks = [loop.run_in_executor(executor, self.process_video, link) for link in self.urls]
            await asyncio.gather(*tasks)

        # clean_folder(self.path_out)


if __name__ == '__main__':
    async def main():
        await UrlToMp3(urls=["https://youtube.com/playlist?list=RDZrXwppk1fbs&playnext=1&si=y__BV-I1zWV5CMva",
                             "https://youtube.com/playlist?list=RDyi6NGtz53K4&playnext=1&si=8usYl6xZUAdCWGcY",
                             "https://youtube.com/playlist?list=RDqRsEjSBhtWo&playnext=1&si=AAw1pkniZVjvftAo"
                             ],
                       path_out=r'C:\Users\dfrty\OneDrive\Рабочий стол\music\test').process()


    asyncio.run(main())
