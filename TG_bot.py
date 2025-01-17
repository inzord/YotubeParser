from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
import os
import logging
import asyncio
from aiogram.fsm.storage.memory import MemoryStorage

from cleaner.clean_folder import bot_clean_folder
from params.params import Params
from yb_to_mp3 import UrlToMp3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=Params().API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message(lambda message: message.text == '/start')
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне ссылки на видео с YouTube, и я отправлю тебе аудиофайлы.")


@dp.message(lambda message: message.text.startswith('http'))
async def handle_youtube_link(message: types.Message):
    await message.reply("Обрабатываю ваши ссылки...")

    urls = message.text.splitlines()
    path_out = Params().PATH_OUT
    audio_files = set()

    try:
        for url in urls:
            if url.startswith('http') and ('youtube.com' in url or 'youtu.be' in url):
                downloader = UrlToMp3(urls=[url], path_out=path_out, max_threads=5)
                downloader.process()

                mp3_files = [f for f in os.listdir(path_out) if f.endswith('.mp3')]
                audio_files.update(mp3_files)

        for mp3_file in audio_files:
            file_path = os.path.join(path_out, mp3_file)
            input_file = FSInputFile(file_path)
            await bot.send_audio(chat_id=message.chat.id, audio=input_file)
        bot_clean_folder(path_out)

        await message.reply("Готово! Аудиофайлы отправлены.")

    except Exception as e:
        logging.error(f"Ошибка при обработке ссылок: {e}")
        await message.reply("Произошла ошибка при обработке ваших ссылок.")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
