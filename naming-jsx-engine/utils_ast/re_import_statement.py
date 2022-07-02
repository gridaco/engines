#
# regex version
#
import re

import_statements_regex = r'''import([ \n\t]*(?:[^ \n\t\{\}]+[ \n\t]*,?)?(?:[ \n\t]*\{(?:[ \n\t]*[^ \n\t"'\{\}]+[ \n\t]*,?)+\})?[ \n\t]*)from[ \n\t]*(['"])([^'"\n]+)(?:['"])'''


def test(txt: str, _import: str, _from: str,):
    try:
        # https://stackoverflow.com/a/69867053/5463235
        variables_imported = re.findall(import_statements_regex, txt)
        for variables, quotes, import_path in variables_imported:
            if _import in variables:
                if import_path == _from:
                    return True
            pass
    except Exception:
        return False
    return False


def contains_js_import_statement(source: str, _import: str, _from: str, by_lines=True, regex=True):
    if regex:
        if by_lines:
            for line in source.split('\n'):
                if test(line, _import, _from):
                    return True
        else:
            return test(source, _import, _from)
        return False
    else:
        return f'import {_import} from \'{_from}\'' in source or f'import {_import} from \"{_from}\"' in source


if __name__ == '__main__':
    _ = contains_js_import_statement(
        '''
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};''', 'styled', 'styled-components', regex=False)
    print(_)
