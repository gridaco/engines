import glob
from sources import ARCHIVES_DIR
from os import path

PATTERNS = ['css', 'scss']

# list all files with pattern in the directory
files = glob.glob(
    path.join(ARCHIVES_DIR, '**/*.{}'.format('|'.join(PATTERNS))))


print(len(files))
