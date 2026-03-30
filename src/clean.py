"""
Clears the folders that contian information for the pipeline
"""
import shutil
from pathlib import Path

def clear_directory(directory: Path):
    """Remove all files in a directory."""
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)