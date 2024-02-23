import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from pydantic import BaseModel, HttpUrl, ValidationError
from config import settings
from aiogram.types import FSInputFile
from pytube import YouTube


class UrlValidator(BaseModel):
    url: HttpUrl


dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: types.MessageId):
    await message.reply("Привет! Отправь мне ссылку на YouTube видео, и я отправлю его тебе в ответ.")


@dp.message()
async def download_video(message: types.Message, bot: Bot):
    try:
         UrlValidator(url=message.text)
    except ValidationError:
         await message.reply('Не корректный url')

    await bot.send_message(message.chat.id, "Идет загрузка...")
    yt = YouTube(message.text)
    stream = yt.streams.filter(progressive=True, file_extension='mp4')
    stream.get_highest_resolution().download(filename=f'{message.chat.id}_{yt.title}.mp4')
    await bot.send_video(message.chat.id, video=FSInputFile(f'{message.chat.id}_{yt.title}.mp4'), caption=f"{yt.title}", parse_mode="Markdown")
    os.remove(f"{message.chat.id}_{yt.title}.mp4")

async def main():
    bot = Bot(settings.TOKEN)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())