def contains_dependency(path, name):
    '''
    Returns True if the dependency is found in the package.json file.
    '''

    # read the package.json file
    with open(path, 'r') as f:
        contents = f.read()

    # parse the json
    json = json.loads(contents)

    # check if the dependency is found in the package.json file
    return name in json['dependencies']


def contains_dev_dependency(path, name):
    '''
    Returns True if the dev dependency is found in the package.json file.
    '''

    # read the package.json file
    with open(path, 'r') as f:
        contents = f.read()

    # parse the json
    json = json.loads(contents)

    # check if the dependency is found in the package.json file
    return name in json['devDependencies']
