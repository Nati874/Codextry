import threading
import tkinter as tk
from tkinter import ttk, messagebox

from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress


def download_video(url: str):
    yt = YouTube(url, on_progress_callback=on_progress)
    ys = yt.streams.get_highest_resolution()
    ys.download()
    return yt.title


def download_playlist(url: str):
    pt = Playlist(url)
    count = 0
    for video in pt.videos:
        ys = video.streams.get_highest_resolution()
        ys.download()
        count += 1
    return count


def download_audio_playlist(url: str):
    pt = Playlist(url)
    count = 0
    for video in pt.videos:
        ys = video.streams.get_audio_only()
        ys.download(mp3=True)
        count += 1
    return count


def download_audio(url: str):
    yt = YouTube(url, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()
    ys.download(mp3=True)
    return yt.title


class YouTubeDownloaderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("780x380")

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        self.audio_entry = self._build_panel(
            container,
            title="Audio",
            row=0,
            col=0,
            action=lambda: self._run_download(
                "Audio", self.audio_entry.get(), download_audio, "audio"
            ),
        )

        self.video_entry = self._build_panel(
            container,
            title="Video",
            row=0,
            col=1,
            action=lambda: self._run_download(
                "Video", self.video_entry.get(), download_video, "video"
            ),
        )

        self.audio_playlist_entry = self._build_panel(
            container,
            title="Audio Playlist",
            row=1,
            col=0,
            action=lambda: self._run_download(
                "Audio Playlist",
                self.audio_playlist_entry.get(),
                download_audio_playlist,
                "playlist_audio",
            ),
        )

        self.video_playlist_entry = self._build_panel(
            container,
            title="Video Playlist",
            row=1,
            col=1,
            action=lambda: self._run_download(
                "Video Playlist",
                self.video_playlist_entry.get(),
                download_playlist,
                "playlist_video",
            ),
        )

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(container, textvariable=self.status_var, anchor="w")
        status_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _build_panel(self, parent, title: str, row: int, col: int, action):
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        parent.rowconfigure(row, weight=1)
        frame.columnconfigure(0, weight=1)

        entry = ttk.Entry(frame)
        entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        button = ttk.Button(frame, text="Download", command=action)
        button.grid(row=0, column=1)

        return entry

    def _run_download(self, panel_name: str, url: str, handler, mode: str):
        url = url.strip()
        if not url:
            messagebox.showwarning("Missing URL", f"Please enter a URL in {panel_name}.")
            return

        self.status_var.set(f"Downloading from {panel_name}...")

        def worker():
            try:
                result = handler(url)
                self.root.after(0, lambda: self._on_success(panel_name, mode, result))
            except Exception as exc:  # broad by design for UI error reporting
                self.root.after(0, lambda: self._on_error(panel_name, exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_success(self, panel_name: str, mode: str, result):
        if mode in ("audio", "video"):
            msg = f"{panel_name} downloaded successfully:\n{result}"
        else:
            msg = f"{panel_name} downloaded successfully. Items downloaded: {result}"

        self.status_var.set(f"{panel_name} download completed")
        messagebox.showinfo("Download Complete", msg)

    def _on_error(self, panel_name: str, exc: Exception):
        self.status_var.set(f"{panel_name} download failed")
        messagebox.showerror(
            "Download Failed",
            f"Could not download from {panel_name}.\n\nError: {exc}",
        )


def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
