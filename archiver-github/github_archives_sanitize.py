# 
# sanitize archive file. unzip archive, remove redundant files, and zip it back.
# 

from email.policy import default
from math import ceil
import shutil
import zipfile
import tarfile
import os

from tqdm import tqdm
import github_archives_index as Indexer
import click
from functools import partial
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
import github_unarchives_sanitize as gus
from github_unarchives import unzip_file

mb = 1024 * 1024

def sanitize_archive(file, tmp, out, skipcb):
  # initial file size
  si = os.stat(file).st_size

  if (skipcb(size=si)):
    return

  _ = unzip_file(file=file, dir=tmp, remove=True)
  path = _['final_path']
  mtype = _['type']

  tqdm.write(f'{file} {mtype} {si} {path}')

  gus.remove_redunant_files(path)

  # rezip the archive
  # 1. zip the sanitized dir 
  if mtype == 'application/gzip' or mtype == 'application/x-gzip':
    tar = tarfile.open(out, 'w:gz')
    tar.add(path, arcname=os.path.basename(path))
    tar.close()
  elif mtype == 'application/zip':
    zip = zipfile.ZipFile(out, 'w')
    zip.write(path, arcname=os.path.basename(path))
    zip.close()

  # 2. remove the sanitized dir
  shutil.rmtree(path) # TODO: check me


  # 4. rename the sanitized archive to the original archive (move)


  # TODO: move file dir to out
  # ---
  # file = os.path.join(out, os.path.basename(file))

  # initial file size
  so = os.stat(file).st_size



  tqdm.write(f'saved {ceil((si - so) / mb)}MiB for {file}')



def proc(repo: str, indir: str, indexer: Indexer.Indexer, pbar: tqdm, minsize, outdir: str, tmp: str):
  tqdm.write(repo)
  org = repo.split('/')[0]
  name = repo.split('/')[1]
  file = os.path.join(indir, org, name + '.zip')
  tmp = os.path.join(tmp, org)
  out = os.path.join(outdir, org, name + '.zip')

  def skipper_min_size(size):
    minsizemib = minsize * mb
    return size <= minsizemib

  # try:
  sanitize_archive(file=file, out=out, tmp=tmp, skipcb=skipper_min_size)
  indexer.add(repo)
  # except Exception as e:
    # indexer.add_error(repo)
    # tqdm.write(str(e))

  pbar.update(1)
  pass

@click.command()
@click.option('--archives', default='.', help='Archives dir')
@click.option('--tmpdir', help='temporary directory to extract archives at.')
@click.option('--patterns', type=click.Path(exists=True), help='Patterns file e.g. .gitignore')
@click.option('--minsize', default=3, type=click.INT, help='minsize to process in mib')
@click.option('--threads', default=1, help='Threads count to utilize', type=click.INT)
def main(archives, patterns, threads, minsize, tmpdir):
  archiveslist = Indexer.Indexer(basedir=archives, init=False).read_index(errors=False)
  indexer = Indexer.Indexer(basedir=archives, key='index-sanitized', errkey='index-sanitized-errors', init=True)
  indexes = indexer.read_index(errors=True)
  # targets = archiveslist - index
  targets = [archive for archive in archiveslist if archive not in indexes]
  total = len(targets)


  # read patterns, remove empty lines, remove comments
  patterns = open(patterns, 'r').read().splitlines()
  patterns = [p for p in patterns if p]
  patterns = [p for p in patterns if not p.startswith('#')]


  progress_bar = tqdm(total=total, position=4,
                        leave=True, initial=len(indexes))


  pool = Pool(threads)

  _func = partial(
      proc,
      indir=archives,
      indexer=indexer,
      pbar=progress_bar,
      minsize=minsize,
      # remove_patterns=patterns,
      outdir=archives,
      tmp=tmpdir,
  )

  pool.map(
      _func,
      targets
  )
  pool.terminate()
  pool.join()

  
  pass


if __name__ == "__main__":
  main()
