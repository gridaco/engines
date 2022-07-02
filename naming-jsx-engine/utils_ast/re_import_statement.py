#
# regex version
#
import re


def contains_js_import_statement(source: str, _import: str, _from: str):
    # https://stackoverflow.com/a/69867053/5463235
    import_statements_regex = r'''import([ \n\t]*(?:[^ \n\t\{\}]+[ \n\t]*,?)?(?:[ \n\t]*\{(?:[ \n\t]*[^ \n\t"'\{\}]+[ \n\t]*,?)+\})?[ \n\t]*)from[ \n\t]*(['"])([^'"\n]+)(?:['"])'''
    # $1 imported variables          - must contain "React"
    # $2 quotes used for the import  -
    # $3 import path                 - must be '"react"' or "'react'"

    variables_imported = re.findall(import_statements_regex, source)
    for variables, quotes, import_path in variables_imported:
        if _import in variables:
            print(import_path)
            if import_path == f'{_from}' or import_path == f"{_from}":
                return True

    return False
