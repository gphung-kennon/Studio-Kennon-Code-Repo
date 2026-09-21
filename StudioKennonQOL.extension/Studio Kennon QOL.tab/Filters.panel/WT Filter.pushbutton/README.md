# WT Filter

> Creates colour-coded filters for external, internal and lining wall
> types using `WT-E##`, `WT-I##` and `LT-##` Type Marks.

## What does it do?

**WT Filter** is designed around a more descriptive wall Type Mark
convention:

``` text
WT-E01
WT-E02
WT-E03    External walls

WT-I01
WT-I02
WT-I03    Internal walls

LT-01
LT-02     Lining walls
```

The tool detects those wall types automatically, creates/reuses Revit
Parameter Filters, and applies graphic overrides to selected View
Templates.

``` text
                 WALL TYPES
                     │
                     ▼
              READ TYPE MARK
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      WT-E##       WT-I##       LT-##
        │            │            │
        ▼            ▼            ▼
   Crosshatch      Diagonal      Colour
   + colour        + colour      only
        │            │            │
        └────────────┼────────────┘
                     ▼
             SELECT TEMPLATES
                     │
                     ▼
              APPLY FILTERS
```

------------------------------------------------------------------------

## What wall types are detected?

The accepted Type Mark formats are:

  Pattern    Meaning
  ---------- ---------------
  `WT-E##`   External wall
  `WT-I##`   Internal wall
  `LT-##`    Lining wall

The script actually accepts between **1 and 3 digits**, so examples
include:

``` text
WT-E1
WT-E01
WT-E001

WT-I1
WT-I01
WT-I001

LT-1
LT-01
LT-001
```

The matching is case-insensitive.

### Examples

  Type Mark            Detected?
  -------------------- -----------
  `WT-E01`             ✓
  `WT-I12`             ✓
  `LT-03`              ✓
  `wt-e01`             ✓
  `W1`                 ✕
  `WT-EXT01`           ✕
  `WT-E-01`            ✕
  `External Wall 01`   ✕

------------------------------------------------------------------------

## Graphic system

The tool uses different hatch patterns to distinguish the wall families.

``` text
WT-E##                    WT-I##                    LT-##

┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│ ╲ ╱ ╲ ╱ ╲ ╱ │          │ ╱ ╱ ╱ ╱ ╱ ╱ │          │              │
│ ╱ ╲ ╱ ╲ ╱ ╲ │          │╱ ╱ ╱ ╱ ╱ ╱  │          │    COLOUR    │
│ ╲ ╱ ╲ ╱ ╲ ╱ │          │ ╱ ╱ ╱ ╱ ╱ ╱ │          │              │
└──────────────┘          └──────────────┘          └──────────────┘

  Crosshatch                  Diagonal                  Colour only
```

### WT-E

External walls receive:

-   Automatically generated colour
-   Colour-coded projection lines
-   Colour-coded cut lines
-   Black crosshatch foreground pattern
-   Coloured solid background

The crosshatch pattern is:

``` text
45° + 135°
1.5 mm spacing
```

------------------------------------------------------------------------

### WT-I

Internal walls receive:

-   Automatically generated colour
-   Colour-coded projection lines
-   Colour-coded cut lines
-   Black diagonal foreground pattern
-   Coloured solid background

The diagonal pattern is:

``` text
45°
1.0 mm spacing
```

------------------------------------------------------------------------

### LT

Lining walls receive:

-   Automatically generated colour
-   Colour-coded projection lines
-   Colour-coded cut lines
-   Coloured solid background

No foreground hatch is applied.

------------------------------------------------------------------------

## Colour generation

Each detected Type Mark is assigned a different colour.

The colours are distributed across the colour spectrum rather than
manually assigned.

This means the exact colour may depend on how many matching wall types
are detected.

``` text
WT-E01  ──► Colour A
WT-E02  ──► Colour B
WT-E03  ──► Colour C
WT-I01  ──► Colour D
WT-I02  ──► Colour E
LT-01   ──► Colour F
```

The important purpose of the colours is **visual differentiation**, not
representing a fixed material colour.

------------------------------------------------------------------------

## How to use it

### 1. Check your Type Marks

Before running the tool, make sure wall **Type Marks** follow the
intended convention.

Example:

``` text
WT-E01
WT-E02
WT-E03

WT-I01
WT-I02

LT-01
LT-02
```

The tool reads the **Type Mark** from the Wall Type.

------------------------------------------------------------------------

### 2. Run WT Filter

The tool scans the project for matching wall types.

You do not need to select the walls manually.

``` text
All Wall Types
       │
       ▼
   Type Mark?
       │
   ┌───┼────────────┐
   ▼   ▼            ▼
 WT-E WT-I         LT
   │   │            │
   └───┴────────────┘
           │
           ▼
      Create filters
```

------------------------------------------------------------------------

### 3. Select View Template(s)

Select one or more View Templates.

``` text
┌─────────────────────────────────────┐
│ Select View Template(s)              │
├─────────────────────────────────────┤
│ ☑ Wall Plans                         │
│ ☑ GA Plans                           │
│ ☐ Documentation                      │
│ ☐ Presentation                       │
│                                     │
│                         [ Select ]   │
└─────────────────────────────────────┘
```

The tool applies the filters and graphic overrides to those templates.

------------------------------------------------------------------------

## Revit filters

A separate Parameter Filter is created/reused for each Type Mark.

For example:

``` text
WT-E01
WT-E02
WT-I01
LT-01
```

becomes:

``` text
Parameter Filters
├── WT-E01
├── WT-E02
├── WT-I01
└── LT-01
```

Each filter effectively asks:

``` text
Is Wall Type Mark equal to this value?
```

------------------------------------------------------------------------

## Hatch patterns are reused

The tool checks for existing patterns before creating new ones.

For external walls it looks for:

``` text
Crosshatch Diagonal - 1.5mm
```

and otherwise can create:

``` text
Auto - Crosshatch Diagonal 1.5mm
```

For internal walls it looks for:

``` text
diagonal 1.0
```

and otherwise can create:

``` text
Auto - Diagonal 1.0mm
```

This makes the tool safe to run repeatedly without intentionally
generating a new hatch pattern every time.

------------------------------------------------------------------------

## What does it change?

The selected View Templates receive filter overrides for the detected
wall types.

The overrides can affect:

-   Projection line colour
-   Cut line colour
-   Surface background pattern
-   Surface background colour
-   Cut background pattern
-   Cut background colour
-   Foreground hatch pattern for WT-E / WT-I walls

It does **not** modify:

-   Wall Type Marks
-   Wall names
-   Wall geometry
-   Wall assemblies
-   Materials

------------------------------------------------------------------------

## Why use this instead of manually creating filters?

Without the tool, a project with many wall types could require manually
creating and configuring filters such as:

``` text
WT-E01
WT-E02
WT-E03
WT-E04
WT-I01
WT-I02
LT-01
LT-02
...
```

The tool turns that into:

``` text
Run WT Filter
      │
      ▼
Find matching Type Marks
      │
      ▼
Create / reuse filters
      │
      ▼
Generate colours
      │
      ▼
Configure hatch patterns
      │
      ▼
Select templates
      │
      ▼
Apply everything
```

------------------------------------------------------------------------

## Troubleshooting

### "No wall types found..."

Check the **Type Mark**, not the wall instance Mark.

Correct:

``` text
Wall Type → Type Mark → WT-E01
```

Incorrect expectation:

``` text
Wall instance → Mark → WT-E01
```

### A wall isn't being detected

Check for small naming differences:

``` text
WT-E01    ✓
WT-E-01   ✕
WT-E01A   ✕
WT-E 01   ✕
```

### Colours don't appear

Check that:

1.  The selected View Template controls the active view.
2.  The wall matches one of the generated filters.
3.  The filter has been added to the template.
4.  Another filter isn't overriding the graphics.

------------------------------------------------------------------------

## Summary

**WT Filter** is the automated graphic-filtering tool for the project's
descriptive wall Type Mark convention.

``` text
WT-E##  → External → Crosshatch
WT-I##  → Internal → Diagonal
LT-##   → Lining   → Colour
```

> **Type Mark → Filter → Colour + Hatch → View Template**
