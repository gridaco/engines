import os
import glob
import utils_ast


EXTS = ['.jsx', '.js', '.tsx', '.ts']


def list_styled_components_files(project_path):
    '''
    find files uses styled-components by searching for the import statement
    -> import styled from "styled-components";
    '''

    files = glob.glob(
        project_path + '**/*.{}'.format(''.join(EXTS)), recursive=True)
    print(len(files))
    # find files uses styled-components by searching for the import statement
    # -> import styled from "styled-components";
    styled_components_files = []
    for f in files:
        path = os.path.join(project_path, f)
        if utils_ast.contains_js_import_statement(path, 'styled', 'styled-components') \
                or utils_ast.contains_js_import_statement(path, 'styled', '@emotion/styled'):
            styled_components_files.append(path)

    return styled_components_files
