import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    IMAGE_DIRECTORY = Path(sys.executable).parent / "images"
else:
    IMAGE_DIRECTORY = Path(__file__).parent

ABQ_LOGO_32 = IMAGE_DIRECTORY / "abq_logo-32x20.png"
ABQ_LOGO_64 = IMAGE_DIRECTORY / "abq_logo-64x40.png"
