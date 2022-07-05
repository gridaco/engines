import glob
import os
from tqdm import tqdm
import shutil
from settings import ARCHIVES_DIR

DIR = os.path.dirname(os.path.abspath(__file__))


def remove_redunant_files(path, recursive=True, log=False):
    """
    Remove redunant files from the repository.
    print the removed files.
    """
    remove = [
        # graphics
        '*.png',
        '*.jpg',
        '*.jpeg',
        '*.gif',
        '*.gif',
        '*.ico',
        '*.svg',
        '*.webp',
        '*.webm',
        # zip
        '*.zip',
        '*.gz',
        '*.bz2',
        '*.7z',
        '*.rar',
        '*.tar',
        '*.tgz',
        '*.tbz2',
        '*.tbz',
        '*.tbz2',
        # videos
        "*.mp4",
        "*.mp3",
        "*.mov",
        "*.avi",
        "*.flv",
        "*.wmv",
        "*.wav",
        # python
        '*.py',
        '*.pyc',
        '*.lock',
        # meta
        'package-lock.json',
        "node_modules",
        "dist",
        ".vscode",
        '.DS_Store',
    ]

    if log:
        tqdm.write(f'Removing redunant files from {path}')

    for pattern in remove:
        for file in glob.glob(os.path.join(path, '**/' + pattern), recursive=recursive):
            # if directory, remove it
            if os.path.isdir(file):
                shutil.rmtree(file, ignore_errors=True)
            else:
                try:
                    os.remove(file)
                except FileNotFoundError:
                    pass
            if log:
                tqdm.write(f'rm - {file}')


def clear_empty_directories():
    # TODO: not tested
    # clears empty org directories
    # https://stackoverflow.com/a/47093793/5463235

    i = 0
    for folder in os.walk(ARCHIVES_DIR):
        if i != 0:
            # folder example: ('FOLDER/3', [], ['file'])
            if not folder[2]:
                os.rmdir(folder[0])
                print(f'rm - {folder[0]}')


if __name__ == '__main__':
    # clear_empty_directories()
    dirs = os.listdir(ARCHIVES_DIR)
    bar = tqdm(total=len(dirs), position=0)
    # loop through all directories under the archives directory
    for orgs in dirs:
        org_path = os.path.join(ARCHIVES_DIR, orgs)
        if os.path.isdir(org_path):
            # list repo dirs under the orgs directory
            for repo in os.listdir(org_path):
                # is dir?
                path = os.path.join(org_path, repo)
                if os.path.isdir(path):
                    remove_redunant_files(path, recursive=True, log=True)
                    bar.update(1)
