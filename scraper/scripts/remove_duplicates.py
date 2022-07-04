#
# this is a script for removing duplicate records from json array with givven key.
# the input fule can be significantly big with more than million records. and 100mb+.
# we'll need a sufficient algorithm to remove duplicates.
#

import json
import click
import tqdm


def remove_duplicates_by_key(file, key):
    with open(file, 'r') as f:
        data = json.load(f)
    bar = tqdm.tqdm(total=len(data))
    ids = []
    for d in data:
        if d[key] not in ids:
            ids.append(d[key])
        else:
            continue
        bar.update(1)
    with open(file, 'w') as f:
        json.dump(data, f)
    print(
        f'Total: {len(ids)} from {len(data)}. removed {len(data) - len(ids)} duplicates.')
    print('Done')
    bar.close()
    f.close()


@click.command()
@click.option('--file', type=click.Path(exists=True))
@click.option('--key', type=click.STRING)
def main(file, key):
    remove_duplicates_by_key(file, key)


if __name__ == '__main__':
    main()
