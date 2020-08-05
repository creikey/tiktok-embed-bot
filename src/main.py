import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

import os
import youtube_dl
import shutil
from urlextract import URLExtract
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction
from functools import wraps

DOWNLOADS_DIR = "video_downloads"
MAX_VID_LENGTH = 500

cur_file_counter = 0

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func
    
    return decorator
send_video_action = send_action(ChatAction.UPLOAD_VIDEO)

def download_to_file(url: str, filename: str) -> int:
    ydl_opts = {
        "quiet": True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(url, download=True)
    
    if video_info["duration"] > MAX_VID_LENGTH:
        return 99999

    ydl_opts = {
        "format": "mp4",
        "outtmpl": filename,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.download([url])

@send_video_action
def download(update, context):
    global cur_file_counter
    url_extractor = URLExtract()
    urls = url_extractor.find_urls(update.message.text)
    if len(urls) == 0:
        err = False
        if update.message.reply_to_message == None:
            err = True
        else:
            urls = url_extractor.find_urls(update.message.reply_to_message.text)
        if err or len(urls) == 0:
            update.message.reply_text("Must either reply to a tiktok url or tell me a url")
            return
    url = urls[0]
    filename = f"{cur_file_counter}.mp4"
    logging.debug(f"Downloading from {url}...")
    
    err = download_to_file(url, filename)
    if err == 0:
        cur_file_counter += 1
        update.message.reply_video(open(filename, "rb"), supports_streaming=True)
    elif err == 99999:
        update.message.reply_text(f"Video is too long, must be shorter than {MAX_VID_LENGTH} seconds")
    else:
        update.message.reply_text(f"Could not download, error {err} . Video has to be shorter than 500 seconds. Tell @creikey")


def main():
    with open("token.txt", "r") as token_file:
        updater = Updater(token_file.read(), use_context=True)
    if os.path.exists(DOWNLOADS_DIR):
        shutil.rmtree(DOWNLOADS_DIR)
    os.mkdir(DOWNLOADS_DIR)
    os.chdir(DOWNLOADS_DIR)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("download", download))

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
