# -*- coding: UTF-8 -*-
"""Create view filters (with colors) for ceilings, grouped by their exact
Height Offset From Level value, then apply the filters to one or more
chosen View Templates (typically a Reflected Ceiling Plan template).
"""

import colorsys

from System.Collections.Generic import List

from pyrevit import revit, DB, forms, script

output = script.get_output()
doc = revit.doc

MM_PER_FT = 304.8
# tolerance so floating-point noise doesn't split one real height into two
# separate filters - +/-0.5mm is comfortably tighter than anything meaningful
# on a real ceiling height, but loose enough to absorb rounding error.
EPSILON_FT = 0.5 / MM_PER_FT

CEILING_HEIGHT_PARAM = DB.BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM

# ---------------------------------------------------------------------------
# 1. Collect distinct ceiling heights (rounded to the nearest whole mm)
# ---------------------------------------------------------------------------

ceilings = DB.FilteredElementCollector(doc)\
    .OfCategory(DB.BuiltInCategory.OST_Ceilings)\
    .WhereElementIsNotElementType()\
    .ToElements()

if not ceilings:
    forms.alert("No ceilings found in this project.", exitscript=True)

heights_mm = set()
for c in ceilings:
    p = c.get_Parameter(CEILING_HEIGHT_PARAM)
    if p and p.HasValue:
        val_ft = p.AsDouble()
        heights_mm.add(int(round(val_ft * MM_PER_FT)))

if not heights_mm:
    forms.alert(
        "No ceilings with a Height Offset From Level value were found.",
        exitscript=True
    )

sorted_heights = sorted(heights_mm)

# ---------------------------------------------------------------------------
# 2. Generate distinct, well-spaced colors (evenly spread hues)
# ---------------------------------------------------------------------------

def generate_colors(n):
    colors = []
    for idx in range(n):
        hue = (idx / float(n)) if n else 0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.65, 0.95)
        colors.append(DB.Color(int(r * 255), int(g * 255), int(b * 255)))
    return colors

color_map = dict(zip(sorted_heights, generate_colors(len(sorted_heights))))

# ---------------------------------------------------------------------------
# 3. Create (or reuse) a ParameterFilterElement per distinct height
# ---------------------------------------------------------------------------

ceiling_cat_ids = List[DB.ElementId]()
ceiling_cat_ids.Add(DB.ElementId(DB.BuiltInCategory.OST_Ceilings))

height_param_id = DB.ElementId(CEILING_HEIGHT_PARAM)

existing_filters = {
    f.Name: f for f in DB.FilteredElementCollector(doc)
    .OfClass(DB.ParameterFilterElement)
}

def filter_name_for(mm):
    return "Ceiling Offset {}mm".format(mm)

created_filters = []  # (mm, ParameterFilterElement)

t = DB.Transaction(doc, "Create ceiling height view filters")
t.Start()
try:
    for mm in sorted_heights:
        name = filter_name_for(mm)
        if name in existing_filters:
            pfe = existing_filters[name]
        else:
            value_ft = mm / MM_PER_FT
            rule = DB.ParameterFilterRuleFactory.CreateEqualsRule(
                height_param_id, value_ft, EPSILON_FT
            )
            elem_filter = DB.ElementParameterFilter(rule)
            pfe = DB.ParameterFilterElement.Create(
                doc, name, ceiling_cat_ids, elem_filter
            )
        created_filters.append((mm, pfe))
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
    title='Select View Template(s) to apply the ceiling height filters to',
    multiselect=True
)

if not selected_templates:
    script.exit()

# ---------------------------------------------------------------------------
# 5. Apply filters + solid-color overrides to each selected view template
# ---------------------------------------------------------------------------

t2 = DB.Transaction(doc, "Apply ceiling height filters to view template(s)")
t2.Start()
try:
    # Find "Solid fill" by its IsSolidFill flag, not by name - the name isn't
    # reliable across locales/templates. Prefer a Drafting-target one (used
    # for view-graphic overrides); fall back to a Model-target one if that's
    # all that exists.
    solid_fill = None
    fallback_solid_fill = None
    for fp in DB.FilteredElementCollector(doc).OfClass(DB.FillPatternElement):
        fill_pattern = fp.GetFillPattern()
        if fill_pattern.IsSolidFill:
            if fill_pattern.Target == DB.FillPatternTarget.Drafting:
                solid_fill = fp
                break
            elif fallback_solid_fill is None:
                fallback_solid_fill = fp
    if not solid_fill:
        solid_fill = fallback_solid_fill

    if solid_fill:
        output.print_md(
            "**Debug:** using solid fill pattern `{}` (Id {}, Target: {})".format(
                solid_fill.Name, solid_fill.Id, solid_fill.GetFillPattern().Target
            )
        )
    else:
        output.print_md(
            "**Warning:** no solid fill pattern found in this document at all - "
            "background color will NOT be applied, only line colors."
        )

    for view in selected_templates:
        for mm, pfe in created_filters:
            fid = pfe.Id
            if fid not in view.GetFilters():
                view.AddFilter(fid)

            ogs = DB.OverrideGraphicSettings()
            color = color_map[mm]

            ogs.SetProjectionLineColor(color)
            ogs.SetCutLineColor(color)

            if solid_fill:
                ogs.SetSurfaceBackgroundPatternId(solid_fill.Id)
                ogs.SetSurfaceBackgroundPatternColor(color)
                ogs.SetCutBackgroundPatternId(solid_fill.Id)
                ogs.SetCutBackgroundPatternColor(color)

            view.SetFilterOverrides(fid, ogs)
    t2.Commit()
except Exception as ex:
    t2.RollBack()
    forms.alert("Failed applying filters to view template(s):\n{}".format(ex),
                exitscript=True)

# ---------------------------------------------------------------------------
# 6. Report
# ---------------------------------------------------------------------------

output.print_md("### Ceiling height filters created/applied")
output.print_md("**Applied to:** " + ", ".join(v.Name for v in selected_templates))
output.print_md("| Height Offset | Color (RGB) |")
output.print_md("|---|---|")
for mm, pfe in created_filters:
    c = color_map[mm]
    output.print_md("| {}mm | {}, {}, {} |".format(mm, c.Red, c.Green, c.Blue))