import json
import os
from os import path
import click
import zipfile
import tarfile
import magic
from tqdm import tqdm
from functools import partial
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from github_unarchives_sanitize import remove_redunant_files
from github_archives_index import read_index
import settings
mime = magic.Magic(mime=True)
# mode
# 1. extact only (extracts only files with matching patterns)
# 2. clean after extract (removes files with matching patterns, after extract-all)


def extract_only(file, dir, patterns, name=None):
    """
    @param patterns: list of patterns to match e.g. - ['*.py', '*.pyc']
    """

    type = mime.from_file(file)

    if type == 'application/gzip':
        try:
            file = tarfile.open(file, 'r:gz')
            # extract only files with matching patterns
            for member in file.getmembers():
                for pattern in patterns:
                    if pattern in member.name:
                        file.extract(member, dir)
            if name is not None:
                old_path = path.join(
                    dir, os.path.commonprefix(file.getnames()))
                new_path = path.join(dir, name)
                os.rename(old_path, new_path)
            file.close()
            return True
        except tarfile.ExtractError as e:
            return False

    if type == 'application/zip':
        try:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zipinfos = zip_ref.infolist()
                zipinfo = zipinfos[0]

                # extract only files with matching patterns
                for member in zip_ref.infolist():
                    for pattern in patterns:
                        if pattern in member.filename:
                            zip_ref.extract(member, dir)

                # rename the extracted directory name if name is given
                if name is not None:
                    old_path = path.join(dir, zipinfo.filename)
                    new_path = path.join(dir, name)
                    os.rename(old_path, new_path)

                file.close()
                return True

        except zipfile.BadZipFile as e:
            return False


def unzip_file(file, dir, name=None, remove=False, clean=True, cleaner=remove_redunant_files):
    final_path = None

    type = mime.from_file(file)

    if type == 'application/gzip':
        try:
            # tar.gz if via wget
            file = tarfile.open(file, 'r:gz')
            old_path = path.join(dir, os.path.commonprefix(file.getnames()))
            final_path = old_path
            file.extractall(dir)
            file.close()
            if name is not None:
                new_path = path.join(dir, name)
                final_path = new_path
                os.rename(old_path, new_path)
        except tarfile.ExtractError as e:
            os.remove(file)
            return False

    # zip if via api
    if type == 'application/zip':
        try:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zipinfos = zip_ref.infolist()
                zipinfo = zipinfos[0]
                old_path = path.join(dir, zipinfo.filename)
                final_path = old_path
                zip_ref.extractall(dir)
                # rename the extracted directory name if name is given
                if name is not None:
                    new_path = path.join(dir, name)
                    final_path = new_path
                    os.rename(old_path, new_path)

        except zipfile.BadZipFile as e:
            os.remove(file)
            return False

    if clean:
        cleaner(final_path)

    if remove:
        os.remove(file)

    return True


def proc(progress_bar, archives_dir, unarchives_dir, patterns, name, clean, cleaner):
    pass


@click.command()
@click.option('--archives', default='.', help='Directory to extract archives from')
@click.option('--archives-patterns', default='*.zip, *.tar.gz', help='Pattern to match archives')
@click.option('--mode', default=1, help='Mode: 1. extract only (extracts only files with matching patterns) 2. clean after extract (removes files with matching patterns, after extract-all)')
@click.option('--patterns', default=None, help='file path for line splitted list of patterns to match - e.g. .gitignore')
@click.option('--threads', default=1, help='Threads count to utilize')
@click.option('--total', default=None, help='max count limit to process.')
def main(archives, archives_patterns, root, mode, patterns, threads, total):
    print("THIS IS NOT READY.")
    # orgs = os.listdir(archives)

    archives_patterns = archives_patterns.split(',')
    patterns = open(patterns, 'r').read(
    ).splitlines() if patterns is not None else None

    indexes = read_index(errors=False)

    if total is not None:
        indexes = indexes[:total]

    progress_bar = tqdm(total=total, position=threads+4,
                        leave=True, initial=len(indexes))

    pool = Pool(threads)

    _func = partial(
        proc,
        progress_bar=progress_bar,
        archives_dir=settings.ARCHIVES_DIR,
        # extract=extract,
    )

    pool.map(
        _func,
        indexes
    )
    pool.terminate()
    pool.join()

    pass


if __name__ == '__main__':
    main()
