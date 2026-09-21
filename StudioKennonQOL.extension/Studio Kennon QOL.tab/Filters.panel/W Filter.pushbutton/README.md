# W Filter

> Creates colour-coded wall filters for wall types using the `W1`, `W2`,
> `W3` ... naming convention.

## What does it do?

**W Filter** automatically finds wall types whose **Type Mark** follows
this pattern:

``` text
W1
W2
W3
W4
...
W10
W11
...
```

It then creates or reuses a Revit **Parameter Filter** for each matching
Type Mark and applies those filters to one or more selected **View
Templates**.

Each wall type receives:

-   A distinct colour
-   Matching projection line colour
-   Matching cut line colour
-   A solid colour background
-   A diagonal foreground hatch for **odd-numbered W types**

``` text
             WALL TYPES
                  │
                  ▼
          Type Mark = W##
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
      W1, W3...           W2, W4...
        │                   │
        ▼                   ▼
   Colour + diagonal     Colour + solid
        │                   │
        └─────────┬─────────┘
                  ▼
          SELECT VIEW TEMPLATES
                  │
                  ▼
          APPLY GRAPHICS
```

------------------------------------------------------------------------

## What wall types are detected?

The tool only detects Type Marks matching:

``` regex
^W(\d+)$
```

In practical terms:

  Type Mark   Detected?
  ----------- -----------
  `W1`        ✓
  `W2`        ✓
  `W10`       ✓
  `W99`       ✓
  `w3`        ✓
  `W-1`       ✕
  `WT-E01`    ✕
  `WT-I01`    ✕
  `W01-EXT`   ✕

The comparison is case-insensitive.

------------------------------------------------------------------------

## Odd vs even wall types

The tool uses the wall number to determine the foreground pattern.

``` text
W1   ──► Colour + DIAGONAL
W2   ──► Colour only
W3   ──► Colour + DIAGONAL
W4   ──► Colour only
W5   ──► Colour + DIAGONAL
...
```

Visual concept:

``` text
ODD W TYPES                 EVEN W TYPES

┌──────────────┐            ┌──────────────┐
│ ╱ ╱ ╱ ╱ ╱ ╱ │            │              │
│╱ ╱ ╱ ╱ ╱ ╱  │            │   SOLID      │
│ ╱ ╱ ╱ ╱ ╱ ╱ │            │    COLOUR    │
└──────────────┘            └──────────────┘
     W1, W3...                   W2, W4...
```

The colours are automatically distributed around the colour spectrum so
that different wall types can be visually distinguished.

------------------------------------------------------------------------

## How to use it

### 1. Make sure wall Type Marks are correct

Before running the tool, confirm that your wall types use the expected
naming convention.

For example:

``` text
W1
W2
W3
W4
W5
```

The tool reads the **Wall Type → Type Mark** value, not the wall
instance Mark.

------------------------------------------------------------------------

### 2. Run W Filter

The tool scans all wall types in the project.

It does not require you to manually select the walls.

``` text
Project
│
├── W1  ✓
├── W2  ✓
├── W3  ✓
├── WT-E01  ✕
├── WT-I01  ✕
└── Generic Wall  ✕
```

------------------------------------------------------------------------

### 3. Select View Template(s)

You will be shown a list of Revit View Templates.

Multiple templates can be selected.

``` text
┌────────────────────────────────────┐
│ Select View Template(s)             │
├────────────────────────────────────┤
│ ☑ GA Plans                         │
│ ☑ Wall Plans                       │
│ ☐ Documentation Plan               │
│ ☐ Presentation                     │
│                                    │
│                         [ Select ]  │
└────────────────────────────────────┘
```

The filters are applied directly to the selected templates.

------------------------------------------------------------------------

## What gets created in Revit?

For every detected Type Mark, the tool creates or reuses a
`ParameterFilterElement`.

For example:

``` text
W1
W2
W3
W4
```

creates:

``` text
Parameter Filters
├── W1
├── W2
├── W3
└── W4
```

The filter rule is essentially:

``` text
Wall Type Mark == "W1"
```

and similarly for every other detected W type.

------------------------------------------------------------------------

## Existing filters are reused

The tool checks whether a filter with the required name already exists.

``` text
              Need W1 filter
                    │
                    ▼
             Does "W1" exist?
                /       \
              YES        NO
               │          │
               ▼          ▼
             Reuse      Create
               │          │
               └────┬─────┘
                    ▼
              Apply to template
```

This means repeatedly running the tool should not create another copy of
every W filter.

------------------------------------------------------------------------

## Hatch pattern

For odd-numbered W types, the tool uses a diagonal drafting fill
pattern.

It first looks for:

``` text
diagonal 1.0
```

If that does not exist, it creates:

``` text
Auto - W Filter Diagonal 1.0mm
```

The hatch is black, while the background colour is the automatically
generated wall colour.

------------------------------------------------------------------------

## Colour behaviour

Each detected Type Mark gets a distinct colour.

For example:

  Type Mark   Graphic treatment
  ----------- -------------------
  W1          Colour + diagonal
  W2          Colour
  W3          Colour + diagonal
  W4          Colour
  W5          Colour + diagonal

The exact RGB values are generated automatically each time the tool
builds its colour map.

------------------------------------------------------------------------

## What the tool changes

The tool modifies the selected **View Templates** by adding the
generated filters and setting their graphic overrides.

It changes:

-   Projection line colour
-   Cut line colour
-   Surface background colour
-   Cut background colour
-   Foreground hatch for odd W types

It does **not** rename your wall types.

It does **not** change the Type Mark values.

It does **not** modify the physical wall geometry.

------------------------------------------------------------------------

## Troubleshooting

### "No wall types found..."

Check that your wall Type Marks actually look like:

``` text
W1
W2
W3
```

and not:

``` text
WT-E01
W-01
Wall 01
W1 External
```

Those other naming conventions are handled by different filtering tools.

### The filter exists but doesn't appear to work

Check:

1.  The selected View Template is actually controlling the active view.
2.  The wall's **Type Mark** matches the filter.
3.  The filter has been added to the template.
4.  Another view filter is not overriding the intended appearance.

------------------------------------------------------------------------

## Summary

**W Filter** is intended for projects using the simple numbered wall
convention:

``` text
W1 → W2 → W3 → W4 → ...
```

Its main purpose is **fast visual differentiation of wall types through
View Template filters**.

> **Type Mark → Automatic Filter → Automatic Colour → View Template**
