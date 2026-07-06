import yt_dlp
import threading
import os


class CVDDownloader:
    def __init__(self, progress_callback, status_callback):
        self.progress_callback = progress_callback
        self.status_callback = status_callback

    # === START DOWNLOAD ===#
    def start_download(self, url, download_type, resolution, output_dir):
        self.status_callback("Starting download...")

        thread = threading.Thread(target=self._process_download, args=(
            url, download_type, resolution, output_dir))
        thread.daemon = True
        thread.start()

    # === PROCESS DOWNLOAD ===#
    def _process_download(self, url, download_type, resolution, output_dir):
        try:
            ydl_opts = self._build_opts(download_type, resolution, output_dir)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_callback(
                "Download completed! Please check the storage folder.")
            self.progress_callback(1.0)

        except yt_dlp.utils.DownloadError as e:
            self.status_callback(f"Download error: {e}")
            self.progress_callback(0.0)
        except OSError as e:
            self.status_callback(f"File system error: {e}")
            self.progress_callback(0.0)

    # === BUILD OPTIONS ===#
    def _build_opts(self, download_type, resolution, output_dir):
        opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True
        }
        if download_type == "Audio Only (MP3)":
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif download_type == "Video Only":
            if resolution == "Best":
                opts['format'] = 'bestvideo'
            else:
                res_num = resolution.replace('p', '')
                opts['format'] = f'bestvideo[height<={res_num}]'
        else:
            if resolution == "Best":
                opts['format'] = 'bestvideo+bestaudio/best'
            else:
                res_num = resolution.replace('p', '')
                opts['format'] = f'bestvideo[height<={res_num}]+bestaudio/best'
        return opts

    # === PROGRESS HOOK ===#
    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes:
                percentage = downloaded_bytes / total_bytes
                self.progress_callback(percentage)

                percent_str = f"{percentage * 100:.1f}%"
                speed = d.get('_speed_str', 'N/A').strip()
                eta = d.get('_eta_str', 'N/A').strip()
                self.status_callback(
                    f"Downloading... {percent_str} (Speed: {speed} | Time Remaining: {eta})")

        elif d['status'] == 'finished':
            self.status_callback(
                "Raw file download completed. Combining files (if necessary)...")
