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
        return not any(fnmatch.fnmatch(name, pattern) for pattern in exclude) and \
                        any(fnmatch.fnmatch(name, pattern) for pattern in include)

    if type == 'application/gzip':
        file = tarfile.open(file, 'r:gz')
        # extract only files with matching patterns
        for member in file.getmembers():
            # match name with glob - member.name
            # should not match any of in exclude (fnmatch)
            # should match at least one of in include (fnmatch)
            if matches(member.name):
                file.extract(member, dir)
        if name is not None:
            old_path = path.join(
                dir, os.path.commonprefix(file.getnames()))
            new_path = path.join(dir, name)
            os.rename(old_path, new_path)
        file.close()
        return True


    if type == 'application/zip':
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zipinfos = zip_ref.infolist()
            zipinfo = zipinfos[0]

            # extract only files with matching patterns
            for member in zip_ref.infolist():
                if matches(member.filename):
                    zip_ref.extract(member, dir)

            # rename the extracted directory name if name is given
            if name is not None:
                old_path = path.join(dir, zipinfo.filename)
                new_path = path.join(dir, name)
                os.rename(old_path, new_path)

            file.close()



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


def proc(archive, progress_bar, archives_dir, unarchives_dir, include, exclude, clean):
    try:
        name = archive.split('/')[-1]
        file = path.join(archives_dir, archive, ".zip")
        extract_only(file=file, dir=path.join(unarchives_dir, archive), include=include, exclude=exclude, name=name)
        indexer.add_to_index(archive)
    except Exception as e:
        indexer.add_error(archive)
    progress_bar.update(1)


# python github_unarchives.py --index=/Volumes/DB64/github-public-archives/archives/index --targetdir=/Volumes/other-volume --threads=100 --total=1000

@click.command()
@click.option('--index', default='.', help='Archives index file')
@click.option('--mode', default=1, help='Mode: 1. extract only (extracts only files with matching patterns) 2. clean after extract (removes files with matching patterns, after extract-all)')
@click.option('--patterns', default=None, help='file path for line splitted list of patterns to match - e.g. .gitignore')
@click.option('--threads', default=1, help='Threads count to utilize')
@click.option('--total', default=None, help='max count limit to process.')
@click.option('--targetdir', help='Target directory')
def main(index, mode, patterns, threads, total, targetdir):
    settings.set_unarchives_dir(targetdir)
    archives = read_index_from_file(index)
    global indexer
    indexer = Indexer(basedir=settings.UNARCHIVES_DIR, init=True)
    indexes = indexer.read_index(errors=True)

    _p = json.load(open(patterns))
    include = _p['include']
    exclude = _p['exclude']


    archives = list(set(archives) - set(indexes))
    if total is not None:
        archives = archives[:total]

    progress_bar = tqdm(total=total, position=threads+4,
                        leave=True, initial=len(archives))

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
