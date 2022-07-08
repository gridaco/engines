# Github public repositories archiver

This is a python project for archiving certain interested public repositories from Github, for mostly M/L dataset usage.

## pre-requirements

### Install dependencies

```sh
# deps
brew install libmagic
# venv
pip3 install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Setup : `.env`

```.env
# you have to set your own github personal access token. read below for more info.
GITHUB_ACCESS_TOKEN=<personal-github-access-token>
# you can configure external storage for the archives (Make sure this is a empty directory and a valid, existing directory.)
PUBLIC_GITHUB_ARCHIVES_DIR=<root-directory-to-save-archives>
```

👉 [How to get Github personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## Hardware setups

Full archive of all the public repositories will cost tons of storage and cost.

For this reason, we also support extracting only specific files from the repository, and removing the archive file (.zip / .tar.gz) afterwards. (You might have to customize the code for the best fit your pipeline)

## Disclaimer

Use it at your own risk.

### About Licenses of the archives

For faster archiving, this project will validate the license of the repositories after archiving. (without using any github api, it will lookup for the LICENSE files in the repository)
