import os
from os import path
import click
import zipfile
import tarfile
import magic
from tqdm import tqdm
from github_unarchives_sanitize import remove_redunant_files

# mode
# 1. extact only (extracts only files with matching patterns)
# 2. clean after extract (removes files with matching patterns, after extract-all)


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


@click.command()
@click.option('--archives', default='.', help='Directory to extract archives from')
@click.option('--archives-patterns', default='*.zip, *.tar.gz', help='Pattern to match archives')
@click.option('--mode', default=1, help='Mode: 1. extract only (extracts only files with matching patterns) 2. clean after extract (removes files with matching patterns, after extract-all)')
@click.option('--patterns', default='', help='Comma separated list of patterns to match')
@click.option('--threads', default=1, help='Threads count to utilize')
def main(archives, archives_patterns, root, mode, patterns, threads):
    # orgs = os.listdir(archives)

    # archives_patterns = archives_patterns.split(',')
    # patterns = patterns.split(',')

    pass


if __name__ == '__main__':
    pass
