# Number Parking

> Numbers parking stalls sequentially along a selected driving path.

## What does it do?

**Number Parking** finds parking elements on a selected Revit level,
lets you choose which parking family type(s) should be included, then
numbers those stalls according to their position along a selected path
curve.

The number is written to a Revit parameter of your choice.

``` text
                 SELECT LEVEL
                      │
                      ▼
             Find parking stalls
                      │
                      ▼
          SELECT PARKING TYPE(S)
                      │
                      ▼
             SELECT PATH CURVE
                      │
                      ▼
       Project each stall onto path
                      │
                      ▼
          Sort stalls along path
                      │
                      ▼
            Choose target parameter
                      │
                      ▼
                1 → 2 → 3 → 4 ...
```

## When should I use it?

Use this when parking spaces need a consistent sequence based on their
position along a circulation route.

Typical examples:

-   Carpark bay numbering
-   Basement parking
-   Accessible + standard bays sharing one sequence
-   Numbering bays along a ramp or driveway

------------------------------------------------------------------------

## How to use it

### 1. Select the level

The tool first displays all levels in the project.

Choose the level containing the parking spaces you want to number.

``` text
┌─────────────────────────────┐
│ Select Level                │
├─────────────────────────────┤
│ ○ Level 01                  │
│ ● B1                         │
│ ○ B2                         │
│ ○ Roof                       │
│                             │
│                 [ Select ]   │
└─────────────────────────────┘
```

Only parking elements associated with the selected level are considered.

------------------------------------------------------------------------

### 2. Select parking type(s)

The tool then lists the parking family types found on that level.

You can select **multiple types**.

This is important because the numbering remains one continuous sequence.

``` text
Standard Bay       ─┐
Accessible Bay     ─┼──►  1  2  3  4  5  6
Motorcycle Bay     ─┘
```

For example, if you select:

-   `Carpark - Standard`
-   `Carpark - Accessible`

the numbering does **not** restart when the parking type changes.

------------------------------------------------------------------------

### 3. Select the driving path

The tool asks you to select a **detail line or model line** representing
the path through the carpark.

``` text
                 Driving direction
                         ─────────►

       ┌───┐   ┌───┐   ┌───┐   ┌───┐
       │ 1 │   │ 2 │   │ 3 │   │ 4 │
       └───┘   └───┘   └───┘   └───┘
           \________________________/
                  PATH CURVE
```

The path does not need to pass through the centre of every parking bay.

The tool projects each parking element's representative location onto
the selected curve.

------------------------------------------------------------------------

## How the numbering is calculated

Conceptually, the tool does this:

``` text
Parking bay location
        │
        ▼
   ┌───────────┐
   │ Project   │
   │ onto path │
   └─────┬─────┘
         │
         ▼
 Position along curve
         │
         ▼
     Sort ascending
         │
         ▼
      1, 2, 3, 4...
```

This means the sequence follows the **path curve**, rather than simply
using Revit element IDs or the left-to-right position on screen.

### Example

``` text
                     PATH
        ╭──────────────────────────╮
        │                          │
      [3]                       [1]│
        │                          │
      [4]                       [2]│
        ╰──────────────────────────╯
             ↑
       numbering follows
       the path position
```

------------------------------------------------------------------------

## 4. Choose the parameter

Finally, the tool asks which parameter should receive the number.

The default is:

``` text
Carpark_Number
```

The parameter can be a:

-   **Text** parameter
-   **Integer** parameter
-   **Number** parameter

For example:

``` text
Parameter name:
┌─────────────────────────────┐
│ Carpark_Number              │
└─────────────────────────────┘
```

The resulting values are:

  Parking element     Value
  ----------------- -------
  First                   1
  Second                  2
  Third                   3
  Fourth                  4

------------------------------------------------------------------------

## Important: the path controls the order

The most important thing to understand is that **the selected curve
defines the numbering order**.

If the numbering appears backwards or follows an unexpected route:

1.  Check the direction and geometry of the path.
2.  Check that the selected parking types are correct.
3.  Make sure the path represents the intended driving sequence.

The tool does not try to understand which direction a car should drive.
It simply sorts parking elements by their projected position along the
selected curve.

------------------------------------------------------------------------

## Numbering options

Before choosing the target parameter, the tool asks for three numbering
options:

``` text
Prefix:       [          ]
Starting no.: [ 1        ]
Suffix:       [          ]
```

Prefix and suffix are optional. If both are left blank and the starting
number is `1`, the behaviour is unchanged:

``` text
1
2
3
4
...
```

Examples:

``` text
Prefix = B
Start  = 101
Suffix =

→ B101, B102, B103...
```

``` text
Prefix = P
Start  = 1
Suffix = A

→ P1A, P2A, P3A...
```

The prefix and suffix require the target Revit parameter to be a **Text**
parameter. Integer and Number parameters continue to work when both
prefix and suffix are blank.

------------------------------------------------------------------------

------------------------------------------------------------------------

## What gets skipped?

A parking element can be skipped if the tool cannot determine a usable
location or cannot project that location onto the selected path.

The report will identify skipped element IDs.

``` text
Numbered 42 of 44 stall(s)

⚠ Skipped 2 element(s) with no location/projection:
123456, 123789
```

------------------------------------------------------------------------

## What happens if the parameter cannot be written?

The tool will report parking elements where the chosen parameter:

-   does not exist, or
-   is read-only, or
-   uses an unsupported storage type.

The tool does **not** silently change the family or create a missing
parameter.

------------------------------------------------------------------------

## Recommended workflow

``` text
1. Draw / verify driving path
              │
              ▼
2. Run Number Parking
              │
              ▼
3. Select level
              │
              ▼
4. Select parking type(s)
              │
              ▼
5. Select path
              │
              ▼
6. Set parameter
              │
              ▼
7. Review report
              │
              ▼
8. Check numbering in plan
```

### Best practice

Create a dedicated detail line or model line for the numbering path so
that the intended sequence is obvious and repeatable.

------------------------------------------------------------------------

## Summary

**Number Parking** is a path-based numbering tool.

> **Level → Parking Types → Path → Projection → Sort → Parameter**

It is particularly useful when parking numbers need to follow the
circulation logic of a carpark rather than simple geometric or
element-ID ordering.
