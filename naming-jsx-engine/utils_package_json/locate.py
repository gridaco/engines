import os
import json


def locate_projects(repo_path):
    '''
    Returns a list of paths to all projects in the repo_path.
    TODO: not tested
    TODO: yarn workspace, lerna monorepo meta is not supported
    '''
    try:
        # get all directories in the repo_path
        dirs = [d for d in os.listdir(repo_path) if os.path.isdir(
            os.path.join(repo_path, d))]

        # get all projects in the repo_path
        projects = []
        for d in dirs:
            path = os.path.join(repo_path, d)
            if os.path.exists(os.path.join(path, "package.json")):
                # read package json, run minimal validation
                with open(os.path.join(path, "package.json"), 'r') as f:
                    contents = f.read()
                    _json = json.loads(contents)
                    if 'name' in _json:
                        # add project to list
                        projects.append({'path': path, 'name': _json['name']})

        return projects
    except Exception:
        return []


if __name__ == '__main__':
    # archives directory
    archives_dir = os.path.join(os.path.dirname(
        __file__), '..', 'sources', 'archives')

    all = []
    # loop through all directory under archives directory
    for d in os.listdir(archives_dir):
        path = os.path.join(archives_dir, d)
        if os.path.isdir(path):
            # get all projects in the directory
            projects = locate_projects(path)
            all.extend(projects)
            print(f'{d}: {len(projects)}')
            for p in projects:
                print(p['name'])
    print(f'Total: {len(all)}')
