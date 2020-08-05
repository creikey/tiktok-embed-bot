import youtube_dl

ydl_opts = {
    "format": "mp4",
    "outtmpl": "output.mp4",
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    print(ydl.download(["https://vm.tiktok.com/JjUHpJw/"]))
