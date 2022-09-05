import os

import PyInstaller.__main__

# Download External
PyInstaller.__main__.run([
    "--onefile",
    "--console",
    "--name", "audio-normalize." + ("exe" if os.name == "nt" else "bin"),
    "--distpath", "./dist",
    "--workpath", "./build",
    "--specpath", "./build",
    "./main.py",
])