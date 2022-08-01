# merge archives into single directory

import os
import click
import tqdm
import shutil


# e.g.  - python merge.py --source=/Volumes/data/public-github-archives/archives-migration-queue-from-wdb2tb/archives --target=/Volumes/data/public-github-archives/archives
@click.command()
@click.option('--source', help='source archives directory', type=click.Path(exists=True))
@click.option('--target', help='target archives directory', type=click.Path(exists=True))
@click.option('--clear', help='clears file after copy', default=True, type=click.BOOL)
def main(source, target, clear):
    """
    Assuming target archives dir already contains index info of source archives, this command does not contribute to index modification.
    """
    source_orgs = os.listdir(source)
    orgslen = len(source_orgs)

    pbar = tqdm.tqdm(total=orgslen, position=4)

    for org in source_orgs:
        # list files under org dir e.g. org/project.zip
        source_repos = os.listdir(os.path.join(source, org))
        for file in source_repos:
            # copy file to target dir if target dir doesn't exist
            if not os.path.exists(os.path.join(target, org, file)):
                os.makedirs(os.path.join(target, org), exist_ok=True)
                shutil.copy(os.path.join(source, org, file),
                            os.path.join(target, org, file))
                if clear:
                    os.remove(os.path.join(source, org, file))

        pbar.update(1)


if __name__ == "__main__":
    main()
