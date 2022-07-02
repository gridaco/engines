import pathlib
import os
from os import path
import glob
from dotenv import load_dotenv

load_dotenv(verbose=True)

DIR = pathlib.Path(__file__).parent.resolve()
ARCHIVES_DIR = os.getenv("PUBLIC_GITHUB_ARCHIVES_DIR")
