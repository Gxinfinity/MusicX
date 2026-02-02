from os import path
import yt_dlp

# Global yt-dlp options (SAFE)
ytdl_opts = {
    "outtmpl": "downloads/%(id)s.%(ext)s",
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "merge_output_format": "mp3",
    "geo_bypass": True,
    "nocheckcertificate": True,
    "quiet": True,
    "no_warnings": True,
    "cookiefile": "cookies.txt",
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)


def download(url: str, my_hook):
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            ydl.add_progress_hook(my_hook)

            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)

            # ensure mp3 path
            if not filename.endswith(".mp3"):
                filename = path.splitext(filename)[0] + ".mp3"

            return filename

    except Exception as e:
        print(f"[yt-dlp ERROR] {e}")
        return None