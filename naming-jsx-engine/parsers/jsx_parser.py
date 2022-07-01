import utils_ast

ACCEPTS_EXT = ['.jsx', '.js', '.tsx']


def is_react_file(file_path):
    '''
    Returns True if the file is a React file.
    - by checking the file extension.
    - by checking the file contents. (checking for the import statement) (uses regex)
    '''

    # check if file is a react file
    # 1. check the file extension
    if not file_path.endswith(ACCEPTS_EXT):
        return False

    # 2. check the file contents for the word `import React from "react"` (apply fuzzy search)
    with open(file_path, 'r') as f:
        contents = f.read()
        return utils_ast.contains_js_import_statement(contents, 'React', 'react')
