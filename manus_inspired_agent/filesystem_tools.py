import os
from pathlib import Path
from typing import List

def create_file(path: str, content: str) -> str:
    """
    Creates a new file at the specified path with the given content.
    If the directory does not exist, it will be created.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf-8')
        return f"File created successfully at {path}"
    except Exception as e:
        return f"Error creating file: {e}"

def read_file(path: str) -> str:
    """
    Reads the content of the file at the specified path.
    """
    try:
        p = Path(path)
        if not p.is_file():
            return f"Error: Path {path} is not a file or does not exist."
        return p.read_text(encoding='utf-8')
    except Exception as e:
        return f"Error reading file: {e}"

def append_to_file(path: str, content: str) -> str:
    """
    Appends the given content to the end of the file at the specified path.
    """
    try:
        p = Path(path)
        if not p.is_file():
            return f"Error: Path {path} is not a file or does not exist."
        with p.open("a", encoding="utf-8") as f:
            f.write(content)
        return f"Content appended successfully to {path}"
    except Exception as e:
        return f"Error appending to file: {e}"

def list_files(path: str = ".") -> List[str]:
    """
    Lists all files and directories in the specified path.
    """
    try:
        p = Path(path)
        if not p.is_dir():
            return [f"Error: Path {path} is not a directory or does not exist."]
        return [str(item) for item in p.iterdir()]
    except Exception as e:
        return [f"Error listing files: {e}"]
