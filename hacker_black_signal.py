import pygame
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import threading
import time
import os
import string

import cv2
from PIL import Image, ImageTk

# ================== تنظیمات صوت ==================
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
pygame.mixer.init()

# ================== تنظیمات ویدئو ==================
VIDEO_PATH = "background.mp4"   # مسیر ویدئو
VIDEO_SIZE = (640, 360)         # (width, height)

# ================== اسکن درایو C ==================
def scan_c_root():
    c_drive = "C:\\"
    # desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    # output_file = os.path.join(desktop, "C_ROOT_FOLDERS.txt")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(current_dir, "C_ROOT_FOLDERS.txt")

    try:
        folders = [f for f in os.listdir(c_drive) if os.path.isdir(os.path.join(c_drive, f))]
        with open(output_file, "w", encoding="utf-8") as f:
            for folder in folders:
                f.write(folder + "\n")
        print(f"C drive root folders saved to: {output_file}")
    except Exception as e:
        print(f"Error scanning C drive: {e}")

# ==================================================
class VideoPlayer:
    def __init__(self, label, video_path, size):
        self.label = label
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            raise FileNotFoundError("Video not found or cannot be opened")

        self.width, self.height = size

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.delay = int(1000 / fps) if fps > 0 else 40  # fallback امن

        self.play()

    def play(self):
        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.width, self.height))

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        self.label.imgtk = imgtk
        self.label.config(image=imgtk)

        self.label.after(self.delay, self.play)


class HackerVideoMusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("☠ HACKER BLACK SIGNAL ☠")
        self.root.configure(bg="black")
        self.root.resizable(False, False)

        self.playlist = []
        self.current_index = -1
        self.is_paused = False

        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Hacker.TButton",
            font=("Courier", 9, "bold"),
            foreground="#00ff00",
            background="#111111"
        )
        style.map("Hacker.TButton", background=[("active", "#003300")])

        # ================== ویدئو ==================
        self.video_label = tk.Label(root, bg="black")
        self.video_label.pack(pady=10)

        if Path(VIDEO_PATH).exists():
            self.video_player = VideoPlayer(
                self.video_label,
                VIDEO_PATH,
                VIDEO_SIZE
            )
        else:
            tk.Label(
                self.video_label,
                text=">> VIDEO NOT FOUND <<",
                font=("Courier", 12, "bold"),
                fg="#ff0000",
                bg="black"
            ).pack(pady=100)

        total_height = VIDEO_SIZE[1] + 320
        self.root.geometry(f"{VIDEO_SIZE[0] + 60}x{total_height}")

        # ================== موزیک ==================
        music_frame = tk.Frame(root, bg="black")
        music_frame.pack(pady=10)

        self.title_label = tk.Label(
            music_frame,
            text=">> HACKER AUDIO ENGINE <<",
            font=("Courier", 10, "bold"),
            fg="#00ff41",
            bg="black"
        )
        self.title_label.pack(pady=5)

        self.song_label = tk.Label(
            music_frame,
            text=">> NO TRACK <<",
            font=("Courier", 9),
            fg="#00ff00",
            bg="black",
            wraplength=VIDEO_SIZE[0]
        )
        self.song_label.pack(pady=2)

        self.time_label = tk.Label(
            music_frame,
            text="00:00 / 00:00",
            font=("Courier", 8),
            fg="#008800",
            bg="black"
        )
        self.time_label.pack()

        controls = tk.Frame(music_frame, bg="black")
        controls.pack(pady=10)

        ttk.Button(controls, text=" ◄◄ ", style="Hacker.TButton",
                   command=self.play_previous).grid(row=0, column=0, padx=8)

        self.play_btn = ttk.Button(
            controls,
            text=" ▶ PLAY ",
            style="Hacker.TButton",
            command=self.toggle_play_pause
        )
        self.play_btn.grid(row=0, column=1, padx=8)

        ttk.Button(controls, text=" ■ STOP ", style="Hacker.TButton",
                   command=self.stop).grid(row=0, column=2, padx=8)

        ttk.Button(controls, text=" ►► ", style="Hacker.TButton",
                   command=self.play_next).grid(row=0, column=3, padx=8)

        vol_frame = tk.Frame(music_frame, bg="black")
        vol_frame.pack(pady=5)

        tk.Label(vol_frame, text="VOL:", font=("Courier", 8),
                 fg="#00ff00", bg="black").pack(side=tk.LEFT, padx=10)

        self.volume = ttk.Scale(
            vol_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.change_volume,
            length=VIDEO_SIZE[0] - 100
        )
        self.volume.set(70)
        self.volume.pack(side=tk.LEFT)
        pygame.mixer.music.set_volume(0.7)

        ttk.Button(
            music_frame,
            text="LOAD TRACKS",
            style="Hacker.TButton",
            command=self.add_songs
        ).pack(pady=8)

        list_frame = tk.Frame(music_frame, bg="black")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.playlist_box = tk.Listbox(
            list_frame,
            height=5,
            font=("Courier", 8),
            fg="#00ff00",
            bg="#0a0a0a",
            selectbackground="#003300",
            yscrollcommand=scrollbar.set
        )
        self.playlist_box.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.playlist_box.yview)

        self.playlist_box.bind("<Double-Button-1>", self.on_song_double_click)

        threading.Thread(target=self.update_progress, daemon=True).start()

        # ====== Thread اسکن خودکار درایو C ======
        threading.Thread(target=scan_c_root, daemon=True).start()

    # ---------- Audio logic ----------
    def add_songs(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.m4a *.flac")]
        )
        for file in files:
            if file not in self.playlist:
                self.playlist.append(file)
                self.playlist_box.insert(tk.END, Path(file).name)

        if self.playlist and self.current_index == -1:
            self.current_index = 0
            self.load_and_play()

    def load_and_play(self):
        if 0 <= self.current_index < len(self.playlist):
            file = self.playlist[self.current_index]
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            self.song_label.config(text=f">> {Path(file).name.upper()} <<")
            self.is_paused = False
            self.play_btn.config(text=" ▶ PAUSE ")
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.current_index)
            self.playlist_box.see(self.current_index)

    def toggle_play_pause(self):
        if pygame.mixer.music.get_busy():
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.play_btn.config(text=" ▶ PAUSE ")
            else:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_btn.config(text=" ▶ PLAY ")
        elif self.playlist:
            self.load_and_play()

    def play_next(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.load_and_play()

    def play_previous(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.load_and_play()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_paused = False
        self.play_btn.config(text=" ▶ PLAY ")
        self.time_label.config(text="00:00 / 00:00")

    def change_volume(self, val):
        pygame.mixer.music.set_volume(float(val) / 100)

    def on_song_double_click(self, event):
        sel = self.playlist_box.curselection()
        if sel:
            self.current_index = sel[0]
            self.load_and_play()

    def update_progress(self):
        while True:
            if pygame.mixer.music.get_busy() and not self.is_paused:
                try:
                    length = pygame.mixer.Sound(
                        self.playlist[self.current_index]
                    ).get_length()
                    pos = pygame.mixer.music.get_pos() / 1000
                    mins, secs = int(pos // 60), int(pos % 60)
                    tmins, tsecs = int(length // 60), int(length % 60)
                    self.time_label.config(
                        text=f"{mins:02d}:{secs:02d} / {tmins:02d}:{tsecs:02d}"
                    )
                    if pos >= length - 0.5:
                        self.play_next()
                except:
                    pass
            time.sleep(0.5)


if __name__ == "__main__":
    root = tk.Tk()
    app = HackerVideoMusicPlayer(root)
    root.mainloop()
