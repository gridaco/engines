# 
# sanitize archive file. unzip archive, remove redundant files, and zip it back.
# 

import zipfile
import tarfile
import os

import tqdm
import github_archives_index as Indexer
import click
from functools import partial
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
import github_unarchives_sanitize as gus
from github_unarchives import unzip_file

def sanitize_archive(file, out):
  # initial file size
  si = os.stat(file).st_size

  _ = unzip_file(file, remove=True)
  path = _['final_path']
  mtype = _['type']

  gus.remove_redunant_files(path)

  # rezip the archive
  if mtype == 'application/gzip' or mtype == 'application/x-gzip':
    tar = tarfile.open(out, 'w:gz')
    tar.add(path, arcname=os.path.basename(path))
    tar.close()
  elif mtype == 'application/zip':
    zip = zipfile.ZipFile(out, 'w')
    zip.write(path, arcname=os.path.basename(path))
    zip.close()

  # TODO: move file dir to out
  # ---
  file = os.path.join(out, os.path.basename(file))

  # initial file size
  so = os.stat(file).st_size



  pass


def proc(repo: str, indexer: Indexer.Indexer, pbar: tqdm.tqdm):



  pbar.update(1)
  indexer.add(repo)
  pass

@click.command()
@click.option('--archives', default='.', help='Archives dir')
@click.option('--tmpdir', default='.', help='temporary directory to extract archives at.')
@click.option('--patterns', type=click.Path(exists=True), help='Patterns file e.g. .gitignore')
@click.option('--threads', default=1, help='Threads count to utilize', type=click.INT)
def main(archives, patterns, threads):
  archives = Indexer.Indexer(basedir=archives, init=False).read_index(errors=False)
  indexer = Indexer.Indexer(basedir=archives, key='index-sanitized', errkey='index-sanitized-errors', init=True)
  indexes = indexer.read_index(errors=True)
  
  # targets = archives - index
  targets = [archive for archive in archives if archive not in indexes]
  total = len(targets)

  # read patterns, remove empty lines, remove comments
  patterns = open(patterns, 'r').read().splitlines()
  patterns = [p for p in patterns if p]
  patterns = [p for p in patterns if not p.startswith('#')]


  progress_bar = tqdm.tqdm(total=total, position=4,
                        leave=True, initial=len(indexes))


  pool = Pool(threads)

  _func = partial(
      proc,
      progress_bar=progress_bar,
      remove_patterns=patterns,
      outdir=archives,
  )

  pool.map(
      _func,
      targets
  )
  pool.terminate()
  pool.join()
  
  pass


if __name__ == "__main__":
  pass
