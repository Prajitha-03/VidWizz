import yt_dlp

def download_video(link, output_path="static/temp"):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
download_video("https://youtube.com/shorts/68kyLxIql30?si=I-QDr8FEbOWuM--S")  # Replace with a valid YouTube link