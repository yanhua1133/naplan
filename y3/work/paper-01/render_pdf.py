from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_paper import render_one


if __name__ == "__main__":
    render_one(1)
