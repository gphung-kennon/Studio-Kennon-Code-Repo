# -*- coding: UTF-8 -*-
"""Create view filters (with colors) for wall types matching
WT-E##, WT-I##, LT-## (matched on the Type Mark parameter),
then apply them to one or more chosen View Templates.
"""

import re
import math
import colorsys

from System.Collections.Generic import List

from pyrevit import revit, DB, forms, script

output = script.get_output()
doc = revit.doc

# ---------------------------------------------------------------------------
# 1. Find wall types whose Type Mark matches our naming convention
# ---------------------------------------------------------------------------

PATTERN = re.compile(r'^(WT-E\d{1,3}|WT-I\d{1,3}|LT-\d{1,3})$', re.IGNORECASE)

wall_types = DB.FilteredElementCollector(doc)\
    .OfClass(DB.WallType)\
    .WhereElementIsElementType()\
    .ToElements()

matches = []  # list of (type_mark, WallType)
for wt in wall_types:
    p = wt.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK)
    if not p:
        continue
    mark = p.AsString()
    if mark and PATTERN.match(mark.strip()):
        matches.append((mark.strip(), wt))

if not matches:
    forms.alert(
        "No wall types found with a Type Mark matching "
        "WT-E##, WT-I## or LT-##.",
        exitscript=True
    )

# de-duplicate by type mark (keep first) and sort for consistent color order
seen = {}
for mark, wt in matches:
    if mark not in seen:
        seen[mark] = wt
marks = sorted(seen.keys())

# ---------------------------------------------------------------------------
# 2. Generate distinct, well-spaced colors (evenly spread hues)
# ---------------------------------------------------------------------------

def generate_colors(n):
    colors = []
    for i in range(n):
        hue = (i / float(n)) if n else 0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.95)
        colors.append(DB.Color(int(r * 255), int(g * 255), int(b * 255)))
    return colors

color_map = dict(zip(marks, generate_colors(len(marks))))

# find the "Solid fill" pattern (used for the colored background pattern)
solid_fill = None
for fp in DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement):
    if fp.GetFillPattern().IsSolidFill:
        solid_fill = fp
        break


def find_pattern_exact(name):
    """Exact (case/whitespace-insensitive) name match only - no fuzzy match."""
    target = name.strip().lower()
    for fp in DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement):
        if fp.Name.strip().lower() == target:
            return fp
    return None


MM_TO_FT = 1.0 / 304.8


def mm_to_internal(mm):
    return mm * MM_TO_FT


def make_fill_grid(angle_deg, spacing_mm, origin=None, shift=0.0):
    grid = DB.FillGrid()
    grid.Angle = math.radians(angle_deg)
    grid.Origin = origin if origin is not None else DB.UV(0, 0)
    grid.Offset = mm_to_internal(spacing_mm)
    grid.Shift = shift
    grid.SetSegments(List[float]())  # empty = solid line, no dashes
    return grid


def create_pattern(name, grids, target=DB.FillPatternTarget.Drafting):
    # The FillPattern.Name can only be set via this 5-arg constructor
    # (there's no plain (name, target) overload, and Name isn't settable
    # after a bare FillPattern()). We use the first grid's angle/spacing
    # to satisfy the constructor, then immediately replace the grids with
    # our full list (this doesn't affect the Name that's already set).
    first_grid = grids[0]
    fp = DB.FillPattern(
        name, target, DB.FillPatternHostOrientation.ToHost,
        first_grid.Angle, first_grid.Offset
    )
    fp.SetFillGrids(List[DB.FillGrid](grids))
    return DB.FillPatternElement.Create(doc, fp)


def get_or_create_pattern(preferred_name, auto_name, grids_factory):
    """1) exact match on the 'ideal' project name, 2) exact match on our
    auto-generated name (from a previous run - keeps it idempotent),
    3) otherwise create a new pattern named auto_name."""
    found = find_pattern_exact(preferred_name)
    if found:
        return found, "existing"

    found = find_pattern_exact(auto_name)
    if found:
        return found, "existing"

    new_fp = create_pattern(auto_name, grids_factory())
    return new_fp, "created"


DIAGONAL_PREFERRED_NAME = "diagonal 1.0"
DIAGONAL_AUTO_NAME = "Auto - Diagonal 1.0mm"

CROSSHATCH_PREFERRED_NAME = "Crosshatch Diagonal - 1.5mm"
CROSSHATCH_AUTO_NAME = "Auto - Crosshatch Diagonal 1.5mm"

BLACK = DB.Color(0, 0, 0)

need_crosshatch = any(m.upper().startswith("WT-E") for m in marks)
need_diagonal = any(m.upper().startswith("WT-I") for m in marks)

crosshatch_pattern = None
diagonal_pattern = None
pattern_status = []  # (name, status) for reporting

t_patterns = DB.Transaction(doc, "Ensure wall filter hatch patterns exist")
t_patterns.Start()
try:
    if need_crosshatch:
        crosshatch_pattern, status = get_or_create_pattern(
            CROSSHATCH_PREFERRED_NAME,
            CROSSHATCH_AUTO_NAME,
            lambda: [make_fill_grid(45, 1.5), make_fill_grid(135, 1.5)]
        )
        pattern_status.append((crosshatch_pattern.Name, status))

    if need_diagonal:
        diagonal_pattern, status = get_or_create_pattern(
            DIAGONAL_PREFERRED_NAME,
            DIAGONAL_AUTO_NAME,
            lambda: [make_fill_grid(45, 1.0)]
        )
        pattern_status.append((diagonal_pattern.Name, status))
    t_patterns.Commit()
except Exception as ex:
    t_patterns.RollBack()
    forms.alert("Failed creating hatch patterns:\n{}".format(ex), exitscript=True)


def foreground_pattern_for(mark):
    """Pick the black hatch pattern based on the wall type prefix."""
    m = mark.upper()
    if m.startswith("WT-E"):
        return crosshatch_pattern
    if m.startswith("WT-I"):
        return diagonal_pattern
    return None  # e.g. LT-## lining walls: no foreground pattern override

# ---------------------------------------------------------------------------
# 3. Create (or reuse) a ParameterFilterElement per wall type, Walls category
# ---------------------------------------------------------------------------

wall_cat_ids = List[DB.ElementId]()
wall_cat_ids.Add(DB.ElementId(DB.BuiltInCategory.OST_Walls))

mark_param_id = DB.ElementId(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK)

existing_filters = {
    f.Name: f for f in DB.FilteredElementCollector(doc)
    .OfClass(DB.ParameterFilterElement)
}

created_filters = []  # (mark, ParameterFilterElement)

t = DB.Transaction(doc, "Create wall type view filters")
t.Start()

try:
    for mark in marks:
        filter_name = mark
        if filter_name in existing_filters:
            pfe = existing_filters[filter_name]
        else:
            rule = DB.ParameterFilterRuleFactory.CreateEqualsRule(
                mark_param_id, mark, True
            )
            elem_filter = DB.ElementParameterFilter(rule)
            pfe = DB.ParameterFilterElement.Create(
                doc, filter_name, wall_cat_ids, elem_filter
            )
        created_filters.append((mark, pfe))
    t.Commit()
except Exception as ex:
    t.RollBack()
    forms.alert("Failed creating filters:\n{}".format(ex), exitscript=True)

# ---------------------------------------------------------------------------
# 4. Pick view template(s) to apply the filters to
# ---------------------------------------------------------------------------

templates = [v for v in DB.FilteredElementCollector(doc).OfClass(DB.View)
             if v.IsTemplate]

if not templates:
    forms.alert("No view templates found in this project.", exitscript=True)

selected_templates = forms.SelectFromList.show(
    sorted(templates, key=lambda v: v.Name),
    name_attr='Name',
    title='Select View Template(s) to apply the wall filters to',
    multiselect=True
)

if not selected_templates:
    script.exit()

# ---------------------------------------------------------------------------
# 5. Apply filters + color overrides to each selected view template
# ---------------------------------------------------------------------------

t2 = DB.Transaction(doc, "Apply wall filters to view template(s)")
t2.Start()

try:
    for view in selected_templates:
        for mark, pfe in created_filters:
            fid = pfe.Id
            if fid not in view.GetFilters():
                view.AddFilter(fid)

            ogs = DB.OverrideGraphicSettings()
            color = color_map[mark]

            ogs.SetProjectionLineColor(color)
            ogs.SetCutLineColor(color)

            # foreground: black hatch pattern (crosshatch for EX, diagonal for I)
            fg_pattern = foreground_pattern_for(mark)
            if fg_pattern:
                ogs.SetSurfaceForegroundPatternColor(BLACK)
                ogs.SetSurfaceForegroundPatternId(fg_pattern.Id)
                ogs.SetCutForegroundPatternColor(BLACK)
                ogs.SetCutForegroundPatternId(fg_pattern.Id)

            # background: solid color fill, distinct per wall type
            if solid_fill:
                ogs.SetSurfaceBackgroundPatternColor(color)
                ogs.SetSurfaceBackgroundPatternId(solid_fill.Id)
                ogs.SetCutBackgroundPatternColor(color)
                ogs.SetCutBackgroundPatternId(solid_fill.Id)

            view.SetFilterOverrides(fid, ogs)
    t2.Commit()
except Exception as ex:
    t2.RollBack()
    forms.alert("Failed applying filters to view template(s):\n{}".format(ex),
                exitscript=True)

# ---------------------------------------------------------------------------
# 6. Report
# ---------------------------------------------------------------------------

output.print_md("### Wall type filters created/applied")
output.print_md("**Applied to:** " + ", ".join(v.Name for v in selected_templates))

if pattern_status:
    output.print_md("**Hatch patterns:**")
    for name, status in pattern_status:
        output.print_md("- `{}` ({})".format(name, status))

output.print_md("| Type Mark | Color (RGB) |")
output.print_md("|---|---|")
for mark, pfe in created_filters:
    c = color_map[mark]
    output.print_md("| {} | {}, {}, {} |".format(mark, c.Red, c.Green, c.Blue))