# Ceiling Filter

> Creates colour-coded ceiling filters based on
> `Height Offset From Level`.

## What does it do?

**Ceiling Filter** automatically finds the different ceiling heights in
the project and creates a Revit Parameter Filter for each distinct
height.

It then applies those filters to one or more selected View Templates.

This is particularly useful for **Reflected Ceiling Plans (RCPs)** where
different ceiling heights need to be visually distinguished.

``` text
                ALL CEILINGS
                     │
                     ▼
          Read Height Offset
                     │
                     ▼
        Round to nearest 1 mm
                     │
                     ▼
          Find unique heights
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        2400        2700        3000
          │          │          │
          ▼          ▼          ▼
        Filter      Filter      Filter
          │          │          │
          └──────────┼──────────┘
                     ▼
             SELECT TEMPLATES
                     │
                     ▼
             APPLY COLOURS
```

------------------------------------------------------------------------

## What parameter does it use?

The tool uses Revit's built-in:

**Height Offset From Level**

parameter for ceilings.

It does not use the ceiling's type name or family name.

------------------------------------------------------------------------

## Example

Suppose a project contains ceilings at:

``` text
2400 mm
2400 mm
2400 mm
2700 mm
2700 mm
3000 mm
```

The tool identifies three unique heights:

``` text
2400 mm
2700 mm
3000 mm
```

and creates:

``` text
Ceiling Offset 2400mm
Ceiling Offset 2700mm
Ceiling Offset 3000mm
```

It does not create a separate filter for every ceiling instance.

------------------------------------------------------------------------

## Why are heights rounded?

Revit stores many dimensional values internally in feet.

The tool converts the value to millimetres and rounds it to the nearest
whole millimetre.

``` text
Revit internal value
        │
        ▼
     Convert
       to mm
        │
        ▼
 Round to nearest 1 mm
        │
        ▼
     2400 mm
```

This prevents tiny floating-point differences from producing unnecessary
separate filters.

For example, values that are effectively the same real-world ceiling
height should not become different filters because of tiny internal
numerical differences.

------------------------------------------------------------------------

## How to use it

### 1. Make sure ceilings have valid heights

The tool first scans the project for ceiling elements.

If there are no ceilings, it stops.

If ceilings exist but none have a valid **Height Offset From Level**, it
also stops.

------------------------------------------------------------------------

### 2. Run Ceiling Filter

The tool identifies every distinct ceiling height.

For example:

``` text
Ceilings found
│
├── 2400 mm
├── 2400 mm
├── 2400 mm
├── 2700 mm
├── 2700 mm
├── 3000 mm
└── 3000 mm

             ↓

Unique heights
│
├── 2400 mm
├── 2700 mm
└── 3000 mm
```

------------------------------------------------------------------------

### 3. Select View Template(s)

The tool then asks which View Templates should receive the ceiling
filters.

Multiple templates can be selected.

``` text
┌─────────────────────────────────────┐
│ Select View Template(s)              │
├─────────────────────────────────────┤
│ ☑ RCP - General                      │
│ ☑ RCP - Documentation                │
│ ☐ GA Plan                            │
│ ☐ Presentation                       │
│                                     │
│                         [ Select ]   │
└─────────────────────────────────────┘
```

------------------------------------------------------------------------

## What gets created?

Each unique ceiling height gets a Parameter Filter.

For example:

``` text
Ceiling Offset 2400mm
Ceiling Offset 2700mm
Ceiling Offset 3000mm
```

Each filter effectively means:

``` text
Ceiling Height Offset == 2400 mm
```

or:

``` text
Ceiling Height Offset == 2700 mm
```

etc.

------------------------------------------------------------------------

## Colour coding

Each height receives a different automatically generated colour.

``` text
2400 mm  ──► Colour A
2700 mm  ──► Colour B
3000 mm  ──► Colour C
3300 mm  ──► Colour D
```

The colour is used for:

-   Projection line colour
-   Cut line colour
-   Surface background colour
-   Cut background colour

Conceptually:

``` text
2400 mm
┌──────────────────────┐
│                      │
│       CEILING        │
│                      │
└──────────────────────┘

2700 mm
┌──────────────────────┐
│                      │
│       CEILING        │
│                      │
└──────────────────────┘

3000 mm
┌──────────────────────┐
│                      │
│       CEILING        │
│                      │
└──────────────────────┘

       Different colour
       = different height
```

The exact colours are generated automatically and are intended for
**visual differentiation**, not to represent a fixed project colour
standard.

------------------------------------------------------------------------

## Existing filters are reused

If a filter with the expected name already exists, the tool reuses it.

For example:

``` text
Already exists:
Ceiling Offset 2400mm
```

The tool does not intentionally create another filter with the same
name.

This makes the workflow suitable for running again when the project
develops additional ceiling heights.

------------------------------------------------------------------------

## Applying the graphics

For every selected View Template, the tool:

1.  Adds the height filter if necessary.
2.  Creates graphic overrides.
3.  Assigns the generated colour.
4.  Applies the line colours.
5.  Applies the solid background colour.

``` text
                 View Template
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       2400 mm       2700 mm      3000 mm
        Filter        Filter        Filter
          │            │            │
          ▼            ▼            ▼
       Colour A      Colour B      Colour C
```

------------------------------------------------------------------------

## What the tool does NOT do

It does not change the actual ceiling height.

For example, if a ceiling is at:

``` text
2700 mm
```

the tool will **not** move it to 2400 mm or 3000 mm.

It only changes the way the ceiling is represented through **View
Template filter graphics**.

------------------------------------------------------------------------

## Recommended use

This tool is most useful when ceiling height is an important
coordination or documentation property.

For example:

``` text
RCP

┌─────────────────────────────┐
│                             │
│       2400 mm ceiling       │
│                             │
│              ┌───────────┐  │
│              │ 2700 mm   │  │
│              │ ceiling   │  │
│              └───────────┘  │
│                             │
└─────────────────────────────┘
```

Instead of relying on notes or manually inspecting every ceiling, the
plan provides an immediate visual distinction.

------------------------------------------------------------------------

## Troubleshooting

### "No ceilings found"

There are no ceiling elements in the current Revit project.

### "No ceilings with a Height Offset From Level value were found"

The project contains ceilings, but the built-in ceiling height parameter
could not provide usable values.

### Colours aren't visible

Check:

1.  The selected View Template controls the active view.
2.  The ceiling matches one of the generated height filters.
3.  The filter is present on the template.
4.  Another view filter is overriding the ceiling graphics.

------------------------------------------------------------------------

## Example workflow

``` text
Open project
    │
    ▼
Check ceiling heights
    │
    ▼
Run Ceiling Filter
    │
    ▼
Tool finds:
2400 / 2700 / 3000
    │
    ▼
Select RCP templates
    │
    ▼
Filters + colours applied
    │
    ▼
Review RCP
```

------------------------------------------------------------------------

## Summary

**Ceiling Filter** converts ceiling height information into an
automatically generated visual filtering system.

> **Height Offset → Unique Heights → Filters → Colours → View Template**

It is designed to make different ceiling heights immediately readable in
plans without manually creating and maintaining a filter for every
height.
