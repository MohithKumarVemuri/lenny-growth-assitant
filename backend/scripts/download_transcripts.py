"""
Download and sync transcripts from https://github.com/ChatPRD/lennys-podcast-transcripts
"""
import os
import subprocess
import shutil
from pathlib import Path

REPO_URL = "https://github.com/ChatPRD/lennys-podcast-transcripts.git"
DEST_DIR = Path(__file__).parent.parent / "data" / "cloned_transcripts"

def download_transcripts():
    print(f"[*] Checking transcript archive at {DEST_DIR}...")
    if DEST_DIR.exists() and any(DEST_DIR.iterdir()):
        print(f"[+] Transcripts already present at {DEST_DIR}")
        return True

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[*] Cloning repository from {REPO_URL} (shallow clone)...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(DEST_DIR)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"[+] Successfully cloned repository to {DEST_DIR}")
        return True
    except Exception as e:
        print(f"[!] Warning: Could not clone repo ({e}). Will proceed with bundled seed transcripts.")
        return False

if __name__ == "__main__":
    download_transcripts()
