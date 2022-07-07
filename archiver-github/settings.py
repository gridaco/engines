import pathlib
import os
from os import path
import glob
from dotenv import load_dotenv

load_dotenv(verbose=True)

ARCHIVES_DIR = os.getenv("PUBLIC_GITHUB_ARCHIVES_DIR")
