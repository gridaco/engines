from time import time
from tqdm import tqdm
from os import path
import os
import glob
import settings
import csv  # TODO: make with csv


def index_file_dir():
    return path.join(settings.ARCHIVES_DIR, 'index')


def errors_index_file_dir():
    return path.join(settings.ARCHIVES_DIR, 'index-errors')


def add_error(repo):
    with open(errors_index_file_dir(), 'a') as f:
        f.write(f'{repo}\n')
        f.close()


def read_errors():
    errors = []
    with open(errors_index_file_dir(), 'r') as f:
        for l in f.readlines():
            errors.append(l.strip())
    return errors


def create_index_if_not_exists():
    if not path.exists(index_file_dir()):
        with open(index_file_dir(), 'w') as f:
            f.close()

    if not path.exists(errors_index_file_dir()):
        with open(errors_index_file_dir(), 'w') as f:
            f.close()


def read_index(errors=False):
    indexes = []
    with open(index_file_dir(), 'r') as f:
        for l in f.readlines():
            indexes.append(l.strip())
    if errors:
        return indexes + read_errors()
    return indexes


def add_to_index(repos):
    existing = read_index()
    # make unique set of repos
    repos = sorted(set(existing + repos))
    with open(index_file_dir(), 'a') as f:
        # clear existing
        f.truncate(0)
        # write new
        for repo in repos:
            f.write(f'{repo}\n')
        f.close()


def index():
    _t_1 = time()
    create_index_if_not_exists()

    orgs = os.listdir(settings.ARCHIVES_DIR)

    # glob: get all the .zip files under.
    files = glob.glob(path.join(settings.ARCHIVES_DIR, '*/*.zip'))
    total = len(files)
    bar = tqdm(total=total)
    repos = []
    for file in files:
        org_name = path.dirname(file).split('/')[-1]
        file_name = path.basename(file).split('.zip')[0]
        repo = f'{org_name}/{file_name}'
        repos.append(repo)
        bar.update(1)
    before = len(read_index())
    add_to_index(repos)
    bar.close()
    _t_2 = time()
    print(
        f'New: Indexing.. Total: {total} repos. (was {before}) (took {_t_2 - _t_1} seconds)')


if __name__ == '__main__':
    print('reading from..', settings.ARCHIVES_DIR)
    index()
