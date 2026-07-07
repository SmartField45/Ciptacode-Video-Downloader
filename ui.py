import customtkinter as ctk
from tkinter import filedialog
import os
import sys

from downloader import CVDDownloader


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class CVDApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ciptacode Video Downloader")
        self.geometry("700x450")
        self.resizable(True, True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.iconbitmap(resource_path(os.path.join("assets", "logo.ico")))
        self.setup_ui()

    def setup_ui(self):
        # --- HEADER ---
        self.title_label = ctk.CTkLabel(
            self, text="Ciptacode Video Downloader", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=(30, 20))

        # --- INPUT URL AREA ---
        self.url_entry = ctk.CTkEntry(
            self, width=550, height=40, placeholder_text="Paste YouTube Link Here...")
        self.url_entry.pack(pady=10)

        # --- SETTINGS AREA ---
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.pack(pady=10)

        # Dropdown 1: Download Type
        self.type_var = ctk.StringVar(value="Video + Audio")
        self.type_dropdown = ctk.CTkOptionMenu(
            self.options_frame,
            values=["Video + Audio", "Video Only", "Audio Only (MP3)"],
            variable=self.type_var,
            command=self.on_type_change
        )
        self.type_dropdown.grid(row=0, column=0, padx=10)

        # Dropdown 2: Resolution
        self.res_var = ctk.StringVar(value="Best")
        self.res_dropdown = ctk.CTkOptionMenu(
            self.options_frame,
            values=["Best", "1080p", "720p", "480p", "360p"],
            variable=self.res_var
        )
        self.res_dropdown.grid(row=0, column=1, padx=10)

        # Setting folder path
        self.folder_path = ctk.StringVar(
            value=os.path.expanduser("~/Downloads"))
        self.folder_btn = ctk.CTkButton(self.options_frame, text="Choose Folder", font=ctk.CTkFont(size=12), height=30,
                                        command=self.choose_folder, fg_color="gray50", hover_color="gray40")
        self.folder_btn.grid(row=0, column=2, padx=10)

        # Text Label for showing the selected folder path
        self.folder_label = ctk.CTkLabel(
            self, textvariable=self.folder_path, text_color="gray70", font=ctk.CTkFont(size=12))
        self.folder_label.pack(pady=(0, 20))

        # --- AREA STATUS & PROGRESS BAR ---
        self.progress_bar = ctk.CTkProgressBar(self, width=550)
        self.progress_bar.set(0)  # Mulai dari 0%
        self.progress_bar.pack(pady=5)

        self.status_label = ctk.CTkLabel(
            self, text="Ready to download!", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=5)

        # --- DOWNLOAD BUTTON ---
        self.download_btn = ctk.CTkButton(self, text="DOWNLOAD VIDEO", font=ctk.CTkFont(
            size=15, weight="bold"), height=45, command=self.start_download)
        self.download_btn.pack(pady=20)

    # --- FUNGSI LOGIKA UI ---
    def on_type_change(self, choice):
        if choice == "Audio Only (MP3)":
            self.res_dropdown.configure(state="disabled")
        else:
            self.res_dropdown.configure(state="normal")

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def update_progress(self, percentage):
        self.progress_bar.set(percentage)

    def update_status(self, text):
        self.status_label.configure(text=text)

        if "completed" in text.lower() or "error" in text.lower():
            self.download_btn.configure(state="normal")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.update_status("Error: Link Cannot be empty!")
            return

        # Takes Data from UI
        dl_type = self.type_var.get()
        res = self.res_var.get()
        folder = self.folder_path.get()

        # Disable the download button to prevent multiple clicks
        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.update_status("Preparing download...")

        # Call the download engine
        downloader = CVDDownloader(self.update_progress, self.update_status)
        downloader.start_download(url, dl_type, res, folder)
