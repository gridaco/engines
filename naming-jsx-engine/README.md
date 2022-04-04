Naming engine schema

> JSX

Single layer elements

- Name
- Type
- Tag
- Style

Nested layer elements

- Name
- Type
- Tag
- Style
- Body
- Parent

### Sanitizer

Color classification
Text content classification
Name tokenizer
Font classification (font db)
Remove w/h

Elements & Trees & Remo / Context

### Sources

**Origin source**

- Vanilla html/css
- react projects

**Web crawled source**

- Non compressed html/css

**ext**

- css
  - scss
  - less
  - sass
  - stylus
  - styl
- html
- jsx (react sub files)
  - tsx
  - js (can contain jsx)
  - ts (can contain styles)

```tsx
<button style={{ ...style }}>Click me</button>

// name : null (fallback to 'button')
// type : node
// tag : button
// style : { ...style }
// content: "Click me"
// properties: null
```

```tsx
<StyledButton>Click me</StyledButton>;

const StyledButton = styled.button`
   ...style
`;

// name : StyledButton
// type : node
// tag : button
// style : { ...style }
// content: "Click me"
// properties: null
```

```tsx
<button className="styled-button">Click me</button>

// name : StyledButton
// type : node
// tag : button
// style : { ...style } (find reference of the style)
// content: "Click me"
// properties: null
```

```css
.styled-button {
  ...style;
}

/*  
name: styled-button
type: css
tag: unknonwn
style: { ...style }
properties: //
*/
```

```html
<button style=".">Click me</button>
<button calss=".">Click me</button>

<!-- 
  name: styled-button
  type: css
  tag: unknonwn
  style: { ...style }
  properties: null
 -->
```
