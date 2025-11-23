import os
import random
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QListWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

 
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class FLCL_audio_app(QWidget):
    def __init__(self):
        super().__init__()
        self.first_played_flag = False
        self.songs = [] 
        self.replay_enabled = False  
        self.shuffle_enabled = False
        self.intro_sound()
        self.settings()
        self.main_ui()
        self.style()

    def settings(self):
        self.setWindowTitle("FLCL-PLAYER")
        self.setFixedSize(590, 300)
        self.setWindowIcon(QIcon(resource_path("Images_in_App/canti_icon_app.ico")))

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        x = screen_width - self.width()
        y = screen_height - self.height()
        self.move(x, y-50)

    def intro_sound(self):
        if not self.first_played_flag:
            self.player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.player.setAudioOutput(self.audio_output)
            self.player.setSource(QUrl.fromLocalFile(resource_path("startup_sound.mp3")))
            self.audio_output.setVolume(0.5)
            self.player.mediaStatusChanged.connect(self.handle_song_finished)
            self.player.play()
            self.first_played_flag = True  
            self.intro_playing = True

    def main_ui(self):
        self.spinning_btn_list = QPushButton()
        self.spinning_btn_list.setFixedSize(80, 80)
        self.spinning_btn_list.setIcon(QIcon(resource_path("Images_in_App/Spinning_P.png")))
        self.spinning_btn_list.setIconSize(QSize(80, 80))
        self.spinning_btn_list.clicked.connect(self.toggle_songlist_controls)

        song_now = "..."
        self.header = QLabel(f"Now Playing: {song_now}")

        main_row = QHBoxLayout()
        main_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_row.addWidget(self.spinning_btn_list, alignment=Qt.AlignmentFlag.AlignVCenter)
        main_row.addWidget(self.header, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.songlist_menu = QListWidget()
        self.songlist_menu.setFixedSize(350, 200)
        self.songlist_menu.setStyleSheet("background-color: black; color: #EEC643;")
        self.load_songs()
        self.songlist_menu.itemDoubleClicked.connect(self.play_selected_song)

        self.artwork = QLabel()
        self.artwork.setFixedSize(200, 200)
        self.artwork.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.artwork.setStyleSheet("background-color: black;")

        self.controls_widget = None  
        self.showing_controls = False  

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.songlist_menu)
        bottom_row.addWidget(self.artwork)

        self.bottom_row = bottom_row  
        main_layout = QVBoxLayout()
        main_layout.addLayout(main_row)
        main_layout.addLayout(bottom_row)
        self.setLayout(main_layout)

    def toggle_songlist_controls(self):
        if not self.showing_controls:
            self.bottom_row.removeWidget(self.songlist_menu)
            self.songlist_menu.hide()
            self.playback_controls()
            self.bottom_row.insertWidget(0, self.controls_widget)
            self.showing_controls = True
        else:
            self.bottom_row.removeWidget(self.controls_widget)
            self.controls_widget.hide()
            self.bottom_row.insertWidget(0, self.songlist_menu)
            self.songlist_menu.show()
            self.showing_controls = False

    def playback_controls(self):
        self.controls_widget = QWidget()
        main_layout = QVBoxLayout()
        self.controls_widget.setFixedSize(350, 200)
        self.controls_widget.setStyleSheet("background-color:black")
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.rewind_btn = QPushButton()
        self.rewind_btn.setIcon(QIcon(resource_path("Images_in_App/rewind_btn.png")))

        self.pause_btn = QPushButton()
        self.pause_btn.setIcon(QIcon(resource_path("Images_in_App/pause_btn.png")))

        self.skip_btn = QPushButton()
        self.skip_btn.setIcon(QIcon(resource_path("Images_in_App/forward_btn.png")))
 
        for btn in [self.rewind_btn, self.pause_btn, self.skip_btn]:
            btn.setFixedSize(95, 95)
            btn.setIconSize(QSize(80, 80))
            top_row.addWidget(btn)

        bottom_row = QHBoxLayout()
        bottom_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.shuffle_btn = QPushButton()
        self.shuffle_btn.setIcon(QIcon(resource_path("Images_in_App/shuffle_btn.png")))

        self.replay_btn = QPushButton()
        self.replay_btn.setIcon(QIcon(resource_path("Images_in_App/replay_btn.png")))

        for btn in [self.shuffle_btn, self.replay_btn]:
            btn.setIconSize(QSize(80, 80))
            btn.setFixedSize(95, 95)
            bottom_row.addWidget(btn)

        main_layout.addLayout(top_row)
        main_layout.addLayout(bottom_row)
        self.controls_widget.setLayout(main_layout)

        self.pause_btn.clicked.connect(self.toggle_pause)
        self.skip_btn.clicked.connect(self.skip_song)
        self.rewind_btn.clicked.connect(self.rewind_song)
        self.shuffle_btn.clicked.connect(self.shuffle_next_song)
        self.replay_btn.clicked.connect(self.replay_next_song)   

    def toggle_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.pause_btn.setIcon(QIcon(resource_path("Images_in_App/play_btn.png")))
        else:
            self.player.play()
            self.pause_btn.setIcon(QIcon(resource_path("Images_in_App/pause_btn.png")))

    def skip_song(self):
        if self.shuffle_enabled:
            count = self.songlist_menu.count()
            current_row = self.songlist_menu.currentRow()
            choices = list(range(count))
            if current_row in choices:
                choices.remove(current_row)
            next_row = random.choice(choices) if choices else current_row
        else:
            current_row = self.songlist_menu.currentRow()
            next_row = (current_row + 1) % self.songlist_menu.count()
        
        self.songlist_menu.setCurrentRow(next_row)
        self.play_selected_song(self.songlist_menu.currentItem())

    def rewind_song(self):
        if hasattr(self, "player"):
            if self.player.position() > 10000:  
                self.player.setPosition(0)
            else: 
                current_row = self.songlist_menu.currentRow()
                if current_row == -1:
                    return
                prev_row = (current_row - 1) % self.songlist_menu.count()
                self.songlist_menu.setCurrentRow(prev_row)
                self.play_selected_song(self.songlist_menu.currentItem())

    def shuffle_next_song(self):
        self.shuffle_enabled = not self.shuffle_enabled
        icon = "shuffle_btn_on.png" if self.shuffle_enabled else "shuffle_btn.png"
        self.shuffle_btn.setIcon(QIcon(resource_path(f"Images_in_App/{icon}")))

    def replay_next_song(self):
        self.replay_enabled = not self.replay_enabled
        icon = "replay_btn_on.png" if self.replay_enabled else "replay_btn.png"
        self.replay_btn.setIcon(QIcon(resource_path(f"Images_in_App/{icon}")))

    def handle_song_finished(self, status):
        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return

        if getattr(self, "intro_playing", False):
            self.intro_playing = False
            return 
        
        current_row = self.songlist_menu.currentRow()

        if self.replay_enabled:
            self.player.stop()
            self.player.play()
            return

        if self.shuffle_enabled:
            count = self.songlist_menu.count()
            choices = list(range(count))
            choices.remove(current_row)
            next_row = random.choice(choices)
            self.songlist_menu.setCurrentRow(next_row)
            self.play_selected_song(self.songlist_menu.currentItem())
            return

        next_row = (current_row + 1) % self.songlist_menu.count()
        self.songlist_menu.setCurrentRow(next_row)
        self.play_selected_song(self.songlist_menu.currentItem())

    def load_songs(self):
        folder = resource_path("Songs")
        for file in os.listdir(folder):
            if file.endswith(".mp3"):
                full_path = os.path.join(folder, file)
                self.songs.append(full_path)
                display_name = file.replace(".mp3", "")
                self.songlist_menu.addItem(display_name)

    def play_selected_song(self, item):
        folder = resource_path("Songs")
        filename = item.text() + ".mp3"
        file_path = os.path.join(folder, filename)

        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.play()

        song_name = item.text()
        self.header.setText(f"Now Playing: ⋆{song_name}⋆")
        self.update_album_art(song_name)

    def update_album_art(self, song_name):
        covers = {
            "Sad Sad Kiddie": "album_covers/naota_cover.jpg",
            "Thank You, My Twilight": "album_covers/eri_cover.png",
            "Ride On Shooting Star": "album_covers/haruko_cover.jpg",
            "Sleepy Head": "album_covers/mamimi_cover.jpg",
            "Come Down": "album_covers/haruko_flcl_cover.png",
            "I Think I Can": "album_covers/naota_manga_cover.jpg",
            "Advice": "album_covers/mamimi_doodle.jpg",
            "Stalker": "album_covers/Mamimi_Light.png",
            "Little Busters": "album_covers/Doodle_Cover.jpg",
            "Nightmare": "album_covers/Kitsurubami.jpg",
            "Funny Bunny": "album_covers/Canti_Cat.jpg",
        }

        path = covers.get(song_name)
        if path:
            path = resource_path(path)
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(
                    self.artwork.width(), self.artwork.height(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.artwork.setPixmap(pixmap)
                return
        self.artwork.clear()

    def style(self):
        self.setStyleSheet("""
            QWidget{ background-color:#EEC643; font-family: "consolas"; }
            QLabel{ color:#141414; font-family: "Jersey 15", "consolas" , "sans-serif"; font-size: 30px; }
            QPushButton{ color:#F5F5F5; font-family: "consolas" , "sans-serif"; font-size: 6.5em; padding: 6px; background-color: black; border-radius: 40px;}
        """)

if __name__ == "__main__":
    app = QApplication([])
    main = FLCL_audio_app()
    main.show()
    app.exec()