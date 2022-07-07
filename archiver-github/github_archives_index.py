from tqdm import tqdm
from os import path
import glob
from settings import ARCHIVES_DIR
import csv  # TODO: make with csv

INDEX_FILE = path.join(ARCHIVES_DIR, 'index')
ERRORS_INDEX_FILE = path.join(ARCHIVES_DIR, 'index-errors')


def add_error(repo):
    with open(ERRORS_INDEX_FILE, 'a') as f:
        f.write(f'{repo}\n')
        f.close()


def read_errors():
    errors = []
    with open(ERRORS_INDEX_FILE, 'r') as f:
        for l in f.readlines():
            errors.append(l.strip())
    return errors


def create_index_if_not_exists():
    if not path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'w') as f:
            f.close()

    if not path.exists(ERRORS_INDEX_FILE):
        with open(ERRORS_INDEX_FILE, 'w') as f:
            f.close()


def read_index(errors=False):
    indexes = []
    with open(INDEX_FILE, 'r') as f:
        for l in f.readlines():
            indexes.append(l.strip())
    return indexes + read_errors()


def add_to_index(repos):
    existing = read_index()
    # make unique set of repos
    repos = sorted(set(existing + repos))
    with open(INDEX_FILE, 'a') as f:
        # clear existing
        f.truncate(0)
        # write new
        for repo in repos:
            f.write(f'{repo}\n')
        f.close()


def index():
    create_index_if_not_exists()
    # glob: get all the .zip files under.
    files = glob.glob(path.join(ARCHIVES_DIR, '*/*.zip'))
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
    print(
        f'New: Indexing.. Total: {total} repos. (was {before})')


if __name__ == '__main__':
    print('reading from..', ARCHIVES_DIR)
    index()
