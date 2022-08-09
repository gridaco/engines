import json
import os
from os import path
import fnmatch
import click
import zipfile
import tarfile
import magic
from tqdm import tqdm
from functools import partial
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from github_unarchives_sanitize import remove_redunant_files
from github_archives_index import read_index_from_file, Indexer
import settings

mime = magic.Magic(mime=True)
# mode
# 1. extact only (extracts only files with matching patterns)
# 2. clean after extract (removes files with matching patterns, after extract-all)


indexer: Indexer = None


def extract_only(file, dir, include: list[str], exclude: list[str], name=None):
    """
    @param patterns: list of patterns to match e.g. - ['*.py', '*.pyc']
    """

    type = mime.from_file(file)

    def matches(name):
        # match name with glob - member.name
        # should not match any of in exclude (fnmatch)
        # should match at least one of in include (fnmatch)
        return not any(fnmatch.fnmatch(name, pattern) for pattern in exclude) and \
            any(fnmatch.fnmatch(name, pattern) for pattern in include)

    if type == 'application/gzip' or type == "application/x-gzip":
        tar = tarfile.open(file, 'r:gz')
        # extract only files with matching patterns
        targets = [name for name in tar.getnames() if matches(name)]
        for target in targets:
            tar.extract(target, dir)

        if name is not None:
            old_path = path.join(
                dir, os.path.commonprefix(tar.getnames()))
            new_path = path.join(dir, name)
            os.rename(old_path, new_path)
        tar.close()
        return True

    if type == 'application/zip':
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zipinfos = zip_ref.infolist()
            zipinfo = zipinfos[0]
            # extract only files with matching patterns
            targets = [name for name in zip_ref.namelist() if matches(name)]
            for target in targets:
                zip_ref.extract(target, dir)

            # rename the extracted directory name if name is given
            if name is not None:
                old_path = path.join(dir, zipinfo.filename)
                new_path = path.join(dir, name)
                os.rename(old_path, new_path)

            file.close()
        return True

    raise Exception("unsupported file type: " + type + " " + file)


def unzip_file(file, dir, name=None, remove=False, cleaner=None):
    final_path = None

    type = mime.from_file(file)

    if type == 'application/gzip':
        try:
            # tar.gz if via wget
            tar = tarfile.open(file, 'r:gz')
            old_path = path.join(dir, os.path.commonprefix(tar.getnames()))
            final_path = old_path
            tar.extractall(dir)
            tar.close()
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

    if cleaner is not None:
        cleaner(final_path)

    if remove:
        os.remove(file)

    return {'final_path': final_path, 'type': type}


def proc(archive, progress_bar, archives_dir, unarchives_dir, include, exclude):
    file = path.join(archives_dir, archive + ".zip")
    if not os.path.exists(file):
        # this is a temporary block. the archives dir may not contain all archives since the archives files are fragmented through various directories. this command may still be called while the merge.py is working. so we are not adding file not found to error, safely exist.
        return

    try:
        org = archive.split('/')[0]
        name = archive.split('/')[-1]
        extract_only(file=file, dir=path.join(unarchives_dir, org),
                     include=include, exclude=exclude, name=name)
        tqdm.write("extracted: " + archive)
        indexer.add(archive)
    except Exception as e:
        tqdm.write(str(e))
        indexer.add_error(archive)
    progress_bar.update(1)


# python github_unarchives.py --index=/Volumes/WDB2TB/public-github-archives/archives/index --targetdir=/Volumes/WDB2TB/public-github-archives/unarchives --patterns='/engine/archiver-github/unarchive_patterns/react.json'

@click.command()
@click.option('--index', default='.', help='Archives index file')
@click.option('--mode', default=1, help='Mode: 1. extract only (extracts only files with matching patterns) 2. clean after extract (removes files with matching patterns, after extract-all)')
@click.option('--patterns', default=None, help='file path for line splitted list of patterns to match - e.g. .gitignore')
@click.option('--threads', default=1, help='Threads count to utilize', type=click.INT)
@click.option('--max', default=None, help='max count limit to process.', type=click.INT)
@click.option('--targetdir', help='Target directory')
def main(index, mode, patterns, threads, max, targetdir):
    settings.set_unarchives_dir(targetdir)
    archives = read_index_from_file(index)
    global indexer
    indexer = Indexer(basedir=targetdir, init=True)
    indexes = indexer.read_index(errors=True)

    _p = json.load(open(patterns))
    include = _p['include']
    exclude = _p['exclude']

    total = len(archives)
    archives = list(set(archives) - set(indexes))
    if max is not None:
        archives = archives[:max]

    progress_bar = tqdm(total=total, position=4,
                        leave=True, initial=len(indexes))

    pool = Pool(threads)

    _func = partial(
        proc,
        progress_bar=progress_bar,
        archives_dir=settings.ARCHIVES_DIR,
        unarchives_dir=settings.UNARCHIVES_DIR,
        include=include,
        exclude=exclude
    )

    pool.map(
        _func,
        archives
    )
    pool.terminate()
    pool.join()


if __name__ == '__main__':
    main()
