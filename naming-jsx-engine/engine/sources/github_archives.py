import click
import magic
import json
from github import Github, GithubException
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import requests
from tqdm import tqdm
import pathlib
import os
from os import path
import glob
import zipfile
import tarfile
from settings import ARCHIVES_DIR
from github_archives_sanitize import remove_redunant_files
from github_archives_index import read_index, add_error, index

KB1 = 1024  # 1 Kibibyte
DIR = pathlib.Path(__file__).parent.resolve()
gh = Github(os.environ['GITHUB_ACCESS_TOKEN'])


def _make_desc(repo, l=50):
    raw = f'repo: {repo}'
    if len(raw) > l:
        raw = raw[:l]
    else:
        raw = raw + ' ' * (l - len(raw))
    return raw


def can_skip(repo, indexes):
    if repo in indexes:
        return True
    return False


def download_zip(repo, use_api=True, max_mb=None):
    max_mb_in_bytes = max_mb * KB1 * KB1 if max_mb is not None else None
    fullname = repo
    org_name = repo.split('/')[0]
    repo_name = repo.split('/')[1]
    org_dir = path.join(ARCHIVES_DIR, org_name)
    file = path.join(ARCHIVES_DIR, f'{org_name}/{repo_name}.zip')

    # create directory if it doesn't exist
    try:
        os.makedirs(org_dir)
    except FileExistsError:
        pass

    try:
        if use_api:
            repo = gh.get_repo(repo)
            archive_link = repo.get_archive_link(
                "zipball", repo.default_branch)
        else:
            # use {master} (branch name with main also works. dosnt work viceversa)
            archive_link = f'https://github.com/{fullname}/archive/master.tar.gz'

        response = requests.get(archive_link, stream=True)

        total_size_in_bytes = int(response.headers.get('content-length', 0))

        # if file bigger than <max_mb>mb, pass. (return False)
        if max_mb is not None and (total_size_in_bytes > max_mb_in_bytes):
            return False

        # description's length to 40 (fixed).
        _desc = _make_desc(fullname)
        progress_bar = tqdm(total=total_size_in_bytes,
                            unit='iB', unit_scale=True, leave=False, desc=_desc)

        with open(file, 'wb') as fp:
            for data in response.iter_content(KB1):
                progress_bar.update(len(data))
                fp.write(data)
                # if file is bigger than <max_mb>mb, abort download and remove. (return False)
                # this will not be indexed, which means in the next execution same repo will be canceled after <max_mb>mb (if the arguments are the same)
                if max_mb is not None and (progress_bar.n > max_mb_in_bytes):
                    progress_bar.close()
                    fp.close()
                    os.remove(file)
                    return False
        progress_bar.close()

        return True
    except GithubException:
        return False
    except KeyError:
        return False
    except Exception as e:
        return False


def extract_only():
    pass


def unzip_file(file, dir, name=None, remove=False, clean=True):
    final_path = None

    mime = magic.Magic(mime=True)
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
        remove_redunant_files(final_path)

    if remove:
        os.remove(file)

    return True


def proc(repo, progress_bar, indexes, extract, max_zip_size=None):
    if can_skip(repo, indexes):
        progress_bar.update(1)
        return

    org = repo.split('/')[0]
    repo_name = repo.split('/')[1]
    org_dir = path.join(ARCHIVES_DIR, org)
    file = path.join(ARCHIVES_DIR, f'{org}/{repo_name}.zip')

    if path.exists(org_dir) and len(glob.glob(path.join(org_dir, f'{repo_name}.zip'))) > 0:
        # if directory exists, check if any *.zip file is present under that directory. (with glob)
        if extract:
            unzip_file(file, org_dir, name=repo_name, remove=False)
            # tqdm.write(f'{repo} archived (unzip only)')
    else:
        dl = download_zip(repo, use_api=False, max_mb=max_zip_size)
        if dl:
            if extract:
                unzip_file(file, org_dir, name=repo_name, remove=False)
                # tqdm.write(f'{repo} archived')
        else:
            add_error(repo)
            # tqdm.write(
            #     f'not found: something went wrong. - https://github.com/{repo}')

    progress_bar.update(1)


@click.command()
@click.option('--f', prompt='file path',
              help='json file path containing the list of repositories')
@click.option('--total', default=None, help='max count limit from the input file.')
@click.option('--threads', default=cpu_count(), help='threads count to use.')
@click.option('--max-zip-size', default=None, help='limit the max zip size per request. (mb)', type=int)
@click.option('--extract', default=True, help='rather to extract file after download zip', type=bool)
def main(f, total, threads, extract, max_zip_size):

    repo_set = [x['id']
                for x in json.load(open(f))]

    indexes = read_index(errors=True)
    if total is not None:
        repo_set = repo_set[:total]

    total = len(repo_set)
    print(f'starting archiver... using {threads} threads.')

    progress_bar = tqdm(total=total, position=threads+4, leave=True)

    pool = ThreadPool(threads)
    download_func = partial(proc, progress_bar=progress_bar,
                            indexes=indexes, extract=extract, max_zip_size=max_zip_size)
    results = pool.map(download_func, repo_set)
    pool.close()
    pool.join()


if __name__ == '__main__':
    # example: python3 github_archives.py --f=<input-file.json> --threads=<thread-count>
    # - python3 github_archives.py --f=/Users/softmarshmallow/Documents/Apps/grida/engine/scraper/styled-components.json --threads=36

    index()  # before starting
    main()
    index()  # after complete
