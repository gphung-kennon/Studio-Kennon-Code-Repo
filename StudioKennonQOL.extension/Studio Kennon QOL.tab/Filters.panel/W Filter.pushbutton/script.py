# -*- coding: UTF-8 -*-
"""Create and apply W wall type view filters.

Finds wall types whose Type Mark matches:
    W1, W2, W3 ... W10, W11, etc.

Each W filter receives:
    Odd W  = spectrum colour + diagonal hatch
    Even W = spectrum colour + solid fill

The filters are then applied to one or more user-selected
View Templates.
"""

import re
import math
import colorsys

from System.Collections.Generic import List

from pyrevit import revit, DB, forms, script


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

output = script.get_output()
doc = revit.doc

PATTERN = re.compile(r'^W(\d+)$', re.IGNORECASE)

BLACK = DB.Color(0, 0, 0)


# ---------------------------------------------------------------------------
# 1. Find wall types whose Type Mark matches W<number>
# ---------------------------------------------------------------------------

wall_types = (
    DB.FilteredElementCollector(doc)
    .OfClass(DB.WallType)
    .WhereElementIsElementType()
    .ToElements()
)

matches = []

for wt in wall_types:

    param = wt.get_Parameter(
        DB.BuiltInParameter.ALL_MODEL_TYPE_MARK
    )

    if not param:
        continue

    mark = param.AsString()

    if not mark:
        continue

    mark = mark.strip()

    match = PATTERN.match(mark)

    if match:
        number = int(match.group(1))
        matches.append((mark, number, wt))


if not matches:

    forms.alert(
        "No wall types found with a Type Mark matching W1, W2, W3, etc.",
        exitscript=True
    )


# ---------------------------------------------------------------------------
# 2. De-duplicate and sort numerically
# ---------------------------------------------------------------------------

seen = {}

for mark, number, wt in matches:

    # Keep the first WallType encountered for each Type Mark.
    if mark.upper() not in seen:
        seen[mark.upper()] = (mark, number, wt)


marks_data = list(seen.values())

marks_data.sort(
    key=lambda x: (x[1], x[0].upper())
)

marks = [x[0] for x in marks_data]


# ---------------------------------------------------------------------------
# 3. Generate evenly-spaced spectrum colours
# ---------------------------------------------------------------------------

def generate_colors(count):
    """Generate evenly-spaced colours around the HSV colour wheel."""

    colors = []

    if count <= 0:
        return colors

    for i in range(count):

        hue = i / float(count)

        r, g, b = colorsys.hsv_to_rgb(
            hue,
            0.70,
            0.95
        )

        colors.append(
            DB.Color(
                int(r * 255),
                int(g * 255),
                int(b * 255)
            )
        )

    return colors


color_list = generate_colors(len(marks))

color_map = dict(
    zip(
        [m.upper() for m in marks],
        color_list
    )
)


# ---------------------------------------------------------------------------
# 4. Find existing Fill Pattern Elements
# ---------------------------------------------------------------------------

fill_patterns = list(
    DB.FilteredElementCollector(doc)
    .OfClass(DB.FillPatternElement)
)


# ---------------------------------------------------------------------------
# Solid Fill
# ---------------------------------------------------------------------------

solid_fill = None

for fp in fill_patterns:

    try:

        pattern = fp.GetFillPattern()

        if pattern.IsSolidFill:
            solid_fill = fp
            break

    except Exception:
        continue


if solid_fill is None:

    forms.alert(
        "Could not find a Solid Fill pattern in this project.",
        exitscript=True
    )


# ---------------------------------------------------------------------------
# Exact pattern lookup
# ---------------------------------------------------------------------------

def find_pattern_exact(name):

    target = name.strip().lower()

    for fp in fill_patterns:

        try:

            if fp.Name.strip().lower() == target:
                return fp

        except Exception:
            continue

    return None


# ---------------------------------------------------------------------------
# 5. Ensure diagonal pattern exists
# ---------------------------------------------------------------------------

DIAGONAL_PREFERRED_NAME = "diagonal 1.0"
DIAGONAL_AUTO_NAME = "Auto - W Filter Diagonal 1.0mm"


def mm_to_internal(mm):
    return mm / 304.8


def make_fill_grid(angle_deg, spacing_mm):

    grid = DB.FillGrid()

    grid.Angle = math.radians(angle_deg)

    grid.Origin = DB.UV(0, 0)

    grid.Offset = mm_to_internal(spacing_mm)

    grid.Shift = 0.0

    grid.SetSegments(
        List[float]()
    )

    return grid


def create_pattern(name, grids):

    first_grid = grids[0]

    pattern = DB.FillPattern(
        name,
        DB.FillPatternTarget.Drafting,
        DB.FillPatternHostOrientation.ToHost,
        first_grid.Angle,
        first_grid.Offset
    )

    pattern.SetFillGrids(
        List[DB.FillGrid](grids)
    )

    return DB.FillPatternElement.Create(
        doc,
        pattern
    )


def get_or_create_diagonal():

    # First try the preferred existing project pattern.
    found = find_pattern_exact(
        DIAGONAL_PREFERRED_NAME
    )

    if found:
        return found, "existing"


    # Then look for our automatically-created pattern.
    found = find_pattern_exact(
        DIAGONAL_AUTO_NAME
    )

    if found:
        return found, "existing"


    # Otherwise create it.
    grids = [
        make_fill_grid(45.0, 1.0)
    ]

    new_pattern = create_pattern(
        DIAGONAL_AUTO_NAME,
        grids
    )

    return new_pattern, "created"


diagonal_pattern = None
diagonal_status = None


# ---------------------------------------------------------------------------
# Create/reuse diagonal pattern
# ---------------------------------------------------------------------------

t_pattern = DB.Transaction(
    doc,
    "Ensure W filter diagonal pattern"
)

t_pattern.Start()

try:

    diagonal_pattern, diagonal_status = (
        get_or_create_diagonal()
    )

    t_pattern.Commit()

except Exception as ex:

    t_pattern.RollBack()

    forms.alert(
        "Failed creating the W filter diagonal pattern:\n\n{}".format(ex),
        exitscript=True
    )


# ---------------------------------------------------------------------------
# 6. Create / reuse ParameterFilterElements
# ---------------------------------------------------------------------------

wall_cat_ids = List[DB.ElementId]()

wall_cat_ids.Add(
    DB.ElementId(
        DB.BuiltInCategory.OST_Walls
    )
)


mark_param_id = DB.ElementId(
    DB.BuiltInParameter.ALL_MODEL_TYPE_MARK
)


existing_filters = {
    f.Name: f
    for f in (
        DB.FilteredElementCollector(doc)
        .OfClass(DB.ParameterFilterElement)
    )
}


created_filters = []

created_filter_names = []
existing_filter_names = []
failed_filter_names = []


t_filters = DB.Transaction(
    doc,
    "Create W wall type filters"
)

t_filters.Start()

try:

    for mark in marks:

        filter_name = mark

        if filter_name in existing_filters:

            pfe = existing_filters[filter_name]

            existing_filter_names.append(
                mark
            )

        else:

            try:

                rule = (
                    DB.ParameterFilterRuleFactory
                    .CreateEqualsRule(
                        mark_param_id,
                        mark,
                        True
                    )
                )

                element_filter = (
                    DB.ElementParameterFilter(rule)
                )

                pfe = (
                    DB.ParameterFilterElement.Create(
                        doc,
                        filter_name,
                        wall_cat_ids,
                        element_filter
                    )
                )

                created_filter_names.append(
                    mark
                )

            except Exception as ex:

                failed_filter_names.append(
                    "{} - {}".format(
                        mark,
                        str(ex)
                    )
                )

                continue

        created_filters.append(
            (mark, pfe)
        )

    t_filters.Commit()

except Exception as ex:

    t_filters.RollBack()

    forms.alert(
        "Failed creating W filters:\n\n{}".format(ex),
        exitscript=True
    )


if not created_filters:

    forms.alert(
        "No W filters were available to apply.",
        exitscript=True
    )


# ---------------------------------------------------------------------------
# 7. Pick View Templates
# ---------------------------------------------------------------------------

templates = [
    v
    for v in (
        DB.FilteredElementCollector(doc)
        .OfClass(DB.View)
    )
    if v.IsTemplate
]


if not templates:

    forms.alert(
        "No view templates found in this project.",
        exitscript=True
    )


selected_templates = forms.SelectFromList.show(
    sorted(
        templates,
        key=lambda v: v.Name
    ),
    name_attr='Name',
    title='Select View Template(s) to apply the W filters to',
    multiselect=True
)


if not selected_templates:

    script.exit()


# ---------------------------------------------------------------------------
# 8. Apply filters + graphics to selected View Templates
# ---------------------------------------------------------------------------

applied_count = 0
updated_count = 0
failed_overrides = []


t_apply = DB.Transaction(
    doc,
    "Apply W wall filters to view templates"
)

t_apply.Start()

try:

    for view in selected_templates:

        existing_view_filters = set(
            view.GetFilters()
        )


        for mark, pfe in created_filters:

            fid = pfe.Id


            # ---------------------------------------------------------------
            # Add filter to view template if necessary
            # ---------------------------------------------------------------

            if fid not in existing_view_filters:

                view.AddFilter(fid)

                existing_view_filters.add(fid)

                applied_count += 1


            # ---------------------------------------------------------------
            # Determine colour
            # ---------------------------------------------------------------

            color = color_map[
                mark.upper()
            ]


            # ---------------------------------------------------------------
            # Create graphic override
            # ---------------------------------------------------------------

            ogs = DB.OverrideGraphicSettings()


            # ---------------------------------------------------------------
            # Line colour
            # ---------------------------------------------------------------

            ogs.SetProjectionLineColor(
                color
            )

            ogs.SetCutLineColor(
                color
            )


            # ---------------------------------------------------------------
            # Background = solid colour
            # ---------------------------------------------------------------

            ogs.SetSurfaceBackgroundPatternColor(
                color
            )

            ogs.SetSurfaceBackgroundPatternId(
                solid_fill.Id
            )

            ogs.SetCutBackgroundPatternColor(
                color
            )

            ogs.SetCutBackgroundPatternId(
                solid_fill.Id
            )


            # ---------------------------------------------------------------
            # Odd W = diagonal foreground
            #
            # Even W = no foreground pattern,
            # therefore the solid background remains visible.
            # ---------------------------------------------------------------

            match = PATTERN.match(
                mark.strip()
            )

            number = int(
                match.group(1)
            )


            if number % 2 == 1:

                ogs.SetSurfaceForegroundPatternColor(
                    BLACK
                )

                ogs.SetSurfaceForegroundPatternId(
                    diagonal_pattern.Id
                )

                ogs.SetCutForegroundPatternColor(
                    BLACK
                )

                ogs.SetCutForegroundPatternId(
                    diagonal_pattern.Id
                )


            # ---------------------------------------------------------------
            # Apply override
            # ---------------------------------------------------------------

            try:

                view.SetFilterOverrides(
                    fid,
                    ogs
                )

                updated_count += 1

            except Exception as ex:

                failed_overrides.append(
                    "{} / {} - {}".format(
                        view.Name,
                        mark,
                        str(ex)
                    )
                )


    t_apply.Commit()

except Exception as ex:

    t_apply.RollBack()

    forms.alert(
        "Failed applying W filter graphics:\n\n{}".format(ex),
        exitscript=True
    )


# ---------------------------------------------------------------------------
# 9. Report
# ---------------------------------------------------------------------------

output.print_md(
    "# W Wall Type Filters"
)

output.print_md(
    "**W Wall Types detected:** {}".format(
        len(marks)
    )
)

output.print_md("")

output.print_md(
    "**Applied to:** {}".format(
        ", ".join(
            v.Name
            for v in selected_templates
        )
    )
)

output.print_md("")

output.print_md(
    "### Filter Status"
)

output.print_md(
    "- Created: **{}**".format(
        len(created_filter_names)
    )
)

output.print_md(
    "- Already existed: **{}**".format(
        len(existing_filter_names)
    )
)

if failed_filter_names:

    output.print_md(
        "- Failed: **{}**".format(
            len(failed_filter_names)
        )
    )


output.print_md("")

output.print_md(
    "### Graphics"
)

output.print_md(
    "- Filter overrides updated: **{}**".format(
        updated_count
    )
)

output.print_md(
    "- Diagonal pattern: `{}` ({})".format(
        diagonal_pattern.Name,
        diagonal_status
    )
)

output.print_md(
    "- Solid fill: `{}`".format(
        solid_fill.Name
    )
)

output.print_md("")

output.print_md(
    "### W Type Colour / Pattern Map"
)

output.print_md(
    "| Type Mark | RGB | Pattern |"
)

output.print_md(
    "|---|---|---|"
)


for mark in marks:

    color = color_map[
        mark.upper()
    ]

    match = PATTERN.match(
        mark.strip()
    )

    number = int(
        match.group(1)
    )

    pattern_name = (
        "Diagonal"
        if number % 2 == 1
        else "Solid"
    )

    output.print_md(
        "| {} | {}, {}, {} | {} |".format(
            mark,
            color.Red,
            color.Green,
            color.Blue,
            pattern_name
        )
    )


if failed_filter_names:

    output.print_md("")

    output.print_md(
        "### Filter Creation Failures"
    )

    for item in failed_filter_names:

        output.print_md(
            "- {}".format(item)
        )


if failed_overrides:

    output.print_md("")

    output.print_md(
        "### Override Failures"
    )

    for item in failed_overrides:

        output.print_md(
            "- {}".format(item)
        )