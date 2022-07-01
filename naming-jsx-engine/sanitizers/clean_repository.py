import glob
import os
import shutil

DIR = os.path.dirname(os.path.abspath(__file__))


def remove_redunant_files(path, recursive=True):
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
            print(f'Removed {file}')


if __name__ == '__main__':
    # loop through all directories under the archives directory
    for orgs in os.listdir(os.path.join(DIR, '../sources/archives')):
        org_path = os.path.join(DIR, '../sources/archives', orgs)
        if os.path.isdir(org_path):
            # list repo dirs under the orgs directory
            for repo in os.listdir(org_path):
                # is dir?
                path = os.path.join(org_path, repo)
                if os.path.isdir(path):
                    remove_redunant_files(path, recursive=True)
