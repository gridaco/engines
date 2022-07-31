from time import time
from tqdm import tqdm
from os import path
import os
import settings
import csv  # TODO: make with csv


class Indexer:
    def __init__(self, basedir, init=False) -> None:
        self.basedir = basedir
        if init:
            self.create_index_if_not_exists()

    def index_file_dir(self):
        return path.join(self.basedir, 'index')
    
    def errors_index_file_dir(self):
        return path.join(self.basedir, 'index-errors')

    def add_error(self, repo):
        with open(self.errors_index_file_dir(), 'a') as f:
            f.write(f'{repo}\n')
            f.close()

    def read_errors(self):
        errors = []
        with open(self.errors_index_file_dir(), 'r') as f:
            for l in f.readlines():
                errors.append(l.strip())
        return errors

    def create_index_if_not_exists(self):
        if not path.exists(self.index_file_dir()):
            with open(self.index_file_dir(), 'w') as f:
                f.close()

        if not path.exists(self.errors_index_file_dir()):
            with open(self.errors_index_file_dir(), 'w') as f:
                f.close()


    def read_index(self, errors=False):
        indexes = read_index_from_file(self.index_file_dir())
        if errors:
            return indexes + self.read_errors()
        return indexes


    def add_to_index(self, repos):
        existing = self.read_index()
        # make unique set of repos
        repos = sorted(set(existing + repos))
        with open(self.index_file_dir(), 'a') as f:
            # clear existing
            f.truncate(0)
            # write new
            for repo in repos:
                f.write(f'{repo}\n')
            f.close()



def read_index_from_file(file):
    indexes = []
    with open(file, 'r') as f:
        for l in f.readlines():
            indexes.append(l.strip())
    return indexes



def indexArchives(basedir):

    _t_1 = time()
    
    indexer = Indexer(basedir, init=True)
    orgs = os.listdir(basedir)

    _t_after_listdir = time()

    if _t_1 - _t_after_listdir > 10:
        # log only when listdir takes more than 10 seconds
        print(f'Info: listing orgs took {_t_1 - _t_after_listdir} seconds')

    bar_total = len(orgs)
    bar = tqdm(
        total=bar_total, desc='Indexing under organization directories', leave=False)
    archives_len = 0

    files = []
    for org in orgs:
        # we don't use glob for performance reasons (it can be very slow on hdd drives with large amount of directories)
        for root, dirs, filesunder in os.walk(path.join(basedir, org)):
            for file in filesunder:
                if file.endswith(".zip") or file.endswith(".tar.gz"):
                    archives_len += 1
                    files.append(path.join(root, file))

        bar.set_description(
            f'{str(archives_len).ljust(6)} // Adding from org: {org.ljust(20)}')
        bar.update(1)

    bar.close()

    repos = []
    for file in files:
        org_name = path.dirname(file).split('/')[-1]
        file_name = path.basename(file).split('.zip')[0]
        repo = f'{org_name}/{file_name}'
        repos.append(repo)
    before = len(indexer.read_index())
    indexer.add_to_index(repos)
    _t_2 = time()
    print(
        f'New: Indexing.. Total: {len(repos)} repos. (was {before}) (took {_t_2 - _t_1} seconds)')


if __name__ == '__main__':
    print('reading from..', settings.ARCHIVES_DIR)
    indexArchives(basedir=settings.ARCHIVES_DIR)
