import click
import glob
import os
from os.path import isfile
from tqdm import tqdm
import shutil
import magic
import zipfile
import tarfile
import settings


DIR = os.path.dirname(os.path.abspath(__file__))

REMOVED_META_FILE = '.removed'


def add_meta(path, removed_files=[]):
    # if .removed file does not exists, create.
    if not os.path.exists(os.path.join(path, REMOVED_META_FILE)):
        with open(os.path.join(path, REMOVED_META_FILE), 'w') as f:
            for file in removed_files:
                file_rel_path = os.path.relpath(file, path)
                f.write(file_rel_path + '\n')
            f.close()


def read_meta(path):
    # read .removed file if exists
    try:
        with open(os.path.join(path, REMOVED_META_FILE), 'r') as f:
            removed_files = f.read().splitlines()
            f.close()
            return removed_files
    except Exception:
        return None


patterns_graphics = [
    '*.png',
    '*.jpg',
    '*.jpeg',
    '*.gif',
    '*.gif',
    '*.ico',
    '*.svg',
    '*.webp',
    '*.webm',
]

patterns_zips = [
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
]

patterns_videos = [
    # videos
    "*.mp4",
    "*.mp3",
    "*.mov",
    "*.avi",
    "*.flv",
    "*.wmv",
    "*.wav",
]

patterns_fonts = [
    # fonts
    "*.ttf",
    "*.otf",
    "*.woff",
    "*.woff2",
    "*.eot",
]


patterns_python_ignore = [
    # python
    '*.py',
    '*.pyc',
    '__pycache__',
]


patterns_db = [
    # mongodb
    'journal',
    '*.wt',
]


patterns_node_ignore = [
    'package-lock.json',
    "node_modules",
    '.firebase',
    '.yarn',
    '.next',
    '.netlify',
    'build',
    'dist',
    '*.lock',
    "dist",
]

patterns_misc = [
    # meta
    '.github',
    ".vscode",
    '.DS_Store'
]


patterns_legacy_langs = [
    '*.php',
]

patterns_size_optimized = patterns_graphics + patterns_zips + patterns_videos + \
    patterns_fonts + patterns_python_ignore + patterns_db + patterns_node_ignore
patterns_frontend_source_files_only = patterns_size_optimized + patterns_misc + [
    # backend
    'backend'
] + patterns_legacy_langs


def read_patterns(patterns):
    # if patterns is path, read patterns from the file
    if isinstance(patterns, str):
        with open(patterns, 'r') as f:
            # read each lines, trim, remove line starts with '#' and empty lines
            patterns = [line.strip()
                        for line in f if not line.startswith('#') and line.strip()]
            f.close()
            return patterns
    else:
        return patterns


def remove_redunant_files(path, patterns=patterns_size_optimized, recursive=True, log=False):
    """
    Remove redunant files from the repository.
    print the removed files.
    """

    patterns = read_patterns(patterns)
    # sort dirs to be first than files (file = ends with extension \.(.*?))
    # [dir, file.x, dir2, file.y] -> [dir, dir2, file.x, file.y]
    patterns = sorted(patterns, key=lambda x: x.endswith(
        r'\.(.*?)'), reverse=True)

    if read_meta(path) is not None:
        if log:
            tqdm.write(f'Skip {path} ... Already sanitized')
        return

    size_1 = os.path.getsize(path)

    if log:
        tqdm.write(f'Removing redunant files from {path} - ({size_1}bytes)')

    removed = []
    for pattern in patterns:
        try:
            for file in glob.iglob(os.path.join(path, '**/' + pattern), recursive=recursive):
                # if directory, remove it
                if os.path.isdir(file):
                    shutil.rmtree(file, ignore_errors=True)
                    removed.append(file)
                else:
                    try:
                        os.remove(file)
                        removed.append(file)
                        if log:
                            tqdm.write(f'rm - {file}')
                    except FileNotFoundError:
                        pass
        except TypeError:
            pass
        except Exception as e:
            if log:
                print(e)

    size_2 = os.path.getsize(path)

    if log:
        diff = size_2 - size_1
        if diff > 0:
            tqdm.write(f'Removed {size_2 - size_1} bytes')

        # if size still bigger than 50mib, log it.
        mib = size_2 / 1024 / 1024
        if mib > 50:
            print(f'Large repo warning: {mib} mib for - {path}')

    add_meta(path, removed)


def clear_empty_directories(under=settings.UNARCHIVES_DIR):
    # TODO: not tested
    # clears empty org directories
    # https://stackoverflow.com/a/47093793/5463235

    i = 0
    for folder in os.walk(under):
        if i != 0:
            # folder example: ('FOLDER/3', [], ['file'])
            if not folder[2]:
                os.rmdir(folder[0])
                print(f'rm - {folder[0]}')


def remove_invalid_archives(under=settings.UNARCHIVES_DIR):
    i = 0
    for folder in os.walk(under):
        if i != 0:
            # folder example: ('FOLDER/3', [], ['file'])
            for file in folder[2]:
                remove_if_invalid_archive(os.path.join(folder[0], file))


def remove_if_invalid_archive(file):
    mime = magic.Magic(mime=True)
    type = mime.from_file(file)
    #

    if type == 'application/gzip':
        try:
            file = tarfile.open(file, 'r:gz')
        except tarfile.ExtractError as e:
            os.remove(file)

    # zip if via api
    if type == 'application/zip':
        try:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                if zip_ref.testzip() is not None:
                    os.remove(file)

        except zipfile.BadZipFile:
            os.remove(file)


@click.command()
def main(dir_archives=settings.ARCHIVES_DIR, dir_unarchives=settings.UNARCHIVES_DIR):

    # clear_empty_directories()
    remove_invalid_archives(dir_archives)

    dirs = sorted(os.listdir(settings.ARCHIVES_DIR))
    bar = tqdm(total=len(dirs), position=0)
    # loop through all directories under the archives directory
    for orgs in dirs:
        org_path = os.path.join(settings.ARCHIVES_DIR, orgs)
        if os.path.isdir(org_path):
            # list repo dirs under the orgs directory
            for repo in os.listdir(org_path):
                # is dir?
                path = os.path.join(org_path, repo)
                if os.path.isdir(path):
                    remove_redunant_files(path, recursive=True, log=True)

                    bar.update(1)


if __name__ == '__main__':
    main()
