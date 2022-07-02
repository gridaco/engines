import json
from github import Github, GithubException
import requests
from tqdm import tqdm
import pathlib
import os
from os import path
import glob
import zipfile
# from ..sanitizers import remove_redunant_files


KB1 = 1024  # 1 Kibibyte

gh = Github(os.environ['GITHUB_ACCESS_TOKEN'])

DIR = pathlib.Path(__file__).parent.resolve()
archives_dir = path.join(pathlib.Path(__file__).parent.resolve(), "archives")


def download_zip(repo, file):
    try:
        repo = gh.get_repo(repo)
        archive_link = repo.get_archive_link("zipball", repo.default_branch)
        response = requests.get(archive_link, stream=True)

        total_size_in_bytes = int(response.headers.get('content-length', 0))

        progress_bar = tqdm(total=total_size_in_bytes,
                            unit='iB', unit_scale=True, position=1)

        with open(file, 'wb') as file:
            for data in response.iter_content(KB1):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        return True
    except GithubException:
        return False
    except KeyError:
        return False


def unzip_file(file, dir, name=None, remove=True, clean=True):
    final_path = None
    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zipinfos = zip_ref.infolist()
            zipinfo = zipinfos[0]
            old_path = path.join(dir, zipinfo.filename)
            final_path = old_path
            zip_ref.extractall(dir)
            # rename the extracted directory name if name is given
            if name:
                new_path = path.join(dir, name)
                final_path = new_path
                os.rename(old_path, new_path)

        if remove:
            os.remove(file)
        # if clean:
            # remove_redunant_files(final_path)
    except zipfile.BadZipFile:
        os.remove(file)
        return False


if __name__ == '__main__':

    total = 10000
    repo_set = [x['id']
                for x in json.load(open(path.join(DIR, '../../scraper/styled-components.json')))][:total]
    total = len(repo_set)

    progress_bar = tqdm(total=total, position=0, leave=True)

    for repo in repo_set:
        org = repo.split('/')[0]
        repo_name = repo.split('/')[1]
        org_dir = path.join(archives_dir, org)
        repo_dir = path.join(org_dir, repo_name)
        file = path.join(archives_dir, f'{org}/{repo_name}.zip')

        # create directory if it doesn't exist
        try:
            os.makedirs(org_dir)
        except FileExistsError:
            pass

        if path.exists(repo_dir):
            print(f'{repo} already archived. skipping..')
        elif path.exists(org_dir) and len(glob.glob(path.join(org_dir, f'{repo_name}.zip'))) > 0:
            # if directory exists, check if any *.zip file is present under that directory. (with glob)
            unzip_file(file, org_dir, name=repo_name, remove=False)
            print(f'{repo} archived (unzip only)')
        else:
            dl = download_zip(repo, file)
            if dl:
                unzip_file(file, org_dir, name=repo_name, remove=False)
                print(f'{repo} archived')
            else:
                print(f'{repo} something went wrong. not found')

        progress_bar.update(1)
