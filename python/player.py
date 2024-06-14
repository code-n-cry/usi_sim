import vlc
from pathlib import Path


BASE_DIR = str(Path(__file__).resolve().parent.parent)
player = vlc.MediaPlayer()
