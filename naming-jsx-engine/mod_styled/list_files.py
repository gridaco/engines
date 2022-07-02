import os
import glob
import utils_ast


EXTS = ('jsx', 'js', 'tsx', 'ts')


def list_styled_components_files(project_path):
    '''
    find files uses styled-components by searching for the import statement
    -> import styled from "styled-components";
    '''
    # match one of the extensions
    files = []
    for ext in EXTS:
        files.extend(
            glob.glob(f'**/*.{ext}', root_dir=project_path, recursive=True))

    # find files uses styled-components by searching for the import statement
    # -> import styled from "styled-components";
    styled_components_files = []
    for f in files:
        path = os.path.join(project_path, f)
        try:
            with open(path, 'r') as fp:
                txt = fp.read()
                if utils_ast.contains_js_import_statement(txt, 'styled', 'styled-components', regex=False) or utils_ast.contains_js_import_statement(txt, 'styled', '@emotion/styled', regex=False):
                    styled_components_files.append(path)
        except Exception:
            pass
    return styled_components_files


if __name__ == '__main__':
    print(utils_ast.contains_js_import_statement(
        '''import styled from "styled-components";
const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;''', 'styled', 'styled-components'))
    # print(list_styled_components_files(
    #     '/Volumes/Data/public-github-archives/archives/MileneGJ/projeto13-mywallet-front'))
