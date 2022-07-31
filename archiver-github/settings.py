import pathlib
import os
from os import path
from dotenv import load_dotenv

load_dotenv(verbose=True)

_DIR = pathlib.Path(__file__).parent.absolute()

ARCHIVES_DIR_FALLBACK = os.path.join(_DIR, 'archives')

ARCHIVES_DIR = os.getenv("PUBLIC_GITHUB_ARCHIVES_DIR", ARCHIVES_DIR_FALLBACK)
# load from env 'PUBLIC_GITHUB_UNARCHIVES_DIR', if not set, use same value as ARCHIVES_DIR
UNARCHIVES_DIR = os.getenv("PUBLIC_GITHUB_UNARCHIVES_DIR", ARCHIVES_DIR)


def print_warnings(silent=False):
    if silent:
        return
    if ARCHIVES_DIR == ARCHIVES_DIR_FALLBACK:
        print(
            "WARNING: PUBLIC_GITHUB_ARCHIVES_DIR not set, using default: " + ARCHIVES_DIR)

def set_archives_dir(dir):
    global ARCHIVES_DIR
    ARCHIVES_DIR = dir
    global UNARCHIVES_DIR
    if UNARCHIVES_DIR == ARCHIVES_DIR_FALLBACK:
        UNARCHIVES_DIR = dir

def set_unarchives_dir(dir):
    global UNARCHIVES_DIR
    UNARCHIVES_DIR = dir