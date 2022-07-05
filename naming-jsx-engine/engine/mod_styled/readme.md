# styled-components style jsx naming

## data collection

1. list node projects
2. list packages with react dependency & (styled-components or @emotion/styled dependency)
3. list files under each package, select files with following patterns

- `*.js`
- `*.jsx`
- `*.ts`
- `*.tsx`

4. select files that contains `styled` or `@emotion/styled` import statement
5. list StyledComponentDeclaration with ts ast.

## dataset

- name
- path (relative path to project root)
- style k:v set

## input / output
