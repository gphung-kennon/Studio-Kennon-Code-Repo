# -*- coding: utf-8 -*-
"""Number parking spaces along a selected path curve, in order of position.

Port of the Dynamo graph "Parking - Parameter Control w Spline".

Workflow:
  1. Pick a Level.
  2. Pick which Parking family type to number (only stalls of that type
     get numbered).
  3. Pick a detail line / model line representing the driving path.
  4. Each stall's location is projected onto the path curve and sorted
     by position along it.
  5. Sequential numbers are written to a parameter you choose
     (default: Carpark_Number).
"""

from pyrevit import revit, DB, forms, script

__title__ = "Number\nParking"
__author__ = "Your Name"

doc = revit.doc
output = script.get_output()

# ---------- 1. Pick the level ----------
levels = DB.FilteredElementCollector(doc).OfClass(DB.Level).ToElements()
level_names = sorted([lvl.Name for lvl in levels])

selected_level_name = forms.SelectFromList.show(
    level_names, title="Select Level", button_name="Select"
)
if not selected_level_name:
    script.exit()

level = next(lvl for lvl in levels if lvl.Name == selected_level_name)

# ---------- 2. Collect parking elements on that level ----------
level_filter = DB.ElementLevelFilter(level.Id)
parking_elements = (
    DB.FilteredElementCollector(doc)
    .OfCategory(DB.BuiltInCategory.OST_Parking)
    .WhereElementIsNotElementType()
    .WherePasses(level_filter)
    .ToElements()
)

if not parking_elements:
    forms.alert(
        "No parking elements found on level '{}'.".format(selected_level_name),
        exitscript=True,
    )

# ---------- 3. Pick which parking TYPE(S) to number ----------
# Multi-select so the spline can run through several stall types
# (e.g. standard + accessible) and still get one continuous sequence,
# instead of each type restarting its own count.
type_names = sorted(set(el.Name for el in parking_elements))
selected_types = forms.SelectFromList.show(
    type_names,
    title="Select Parking Type(s) to Number",
    button_name="Select",
    multiselect=True,
)
if not selected_types:
    script.exit()

filtered_parking = [el for el in parking_elements if el.Name in selected_types]

# ---------- 4. Pick the path curve (detail line / model line) ----------
forms.alert(
    "Select the detail line or model line that represents the driving path.",
    ok=True,
)
path_element = revit.pick_element(message="Select path curve")
if not path_element:
    script.exit()

curve = path_element.GeometryCurve
if curve is None:
    forms.alert("Selected element has no usable curve geometry.", exitscript=True)


def get_location_point(el):
    """Return a representative XYZ point for a parking element."""
    loc = el.Location
    if isinstance(loc, DB.LocationPoint):
        return loc.Point
    if isinstance(loc, DB.LocationCurve):
        return loc.Curve.Evaluate(0.5, True)
    bbox = el.get_BoundingBox(None)
    if bbox:
        return (bbox.Min + bbox.Max) / 2
    return None


# ---------- 5. Project each stall onto the path and sort ----------
entries = []
skipped = []
for el in filtered_parking:
    pt = get_location_point(el)
    if pt is None:
        skipped.append(el.Id)
        continue
    proj = curve.Project(pt)
    if proj is None:
        skipped.append(el.Id)
        continue
    entries.append((proj.Parameter, el))

entries.sort(key=lambda pair: pair[0])

# ---------- 6. Ask for numbering options ----------
prefix = forms.ask_for_string(
    default="",
    prompt="Optional prefix (leave blank for numbers only):",
    title="Parking Number Prefix",
)
if prefix is None:
    script.exit()

start_number_text = forms.ask_for_string(
    default="1",
    prompt="Starting number:",
    title="Parking Start Number",
)
if start_number_text is None:
    script.exit()

try:
    start_number = int(start_number_text.strip())
except (ValueError, AttributeError):
    forms.alert("Starting number must be a whole number.", exitscript=True)

suffix = forms.ask_for_string(
    default="",
    prompt="Optional suffix (leave blank for numbers only):",
    title="Parking Number Suffix",
)
if suffix is None:
    script.exit()

# ---------- 7. Ask for the target parameter name ----------
param_name = forms.ask_for_string(
    default="Carpark_Number",
    prompt="Parameter name to write the sequence number to:",
    title="Parameter Name",
)
if not param_name:
    script.exit()

# ---------- 8. Write sequential numbers ----------
failed = []
with revit.Transaction("Number Parking Spaces"):
    for index, (_, el) in enumerate(entries):
        number = start_number + index
        value = "{}{}{}".format(prefix, number, suffix)

        p = el.LookupParameter(param_name)
        if p is None or p.IsReadOnly:
            failed.append(el.Id)
            continue
        if p.StorageType == DB.StorageType.String:
            p.Set(value)
        elif p.StorageType == DB.StorageType.Integer:
            # Prefix/suffix cannot be represented by numeric Revit parameters.
            # Preserve the existing numeric behaviour only when both are blank.
            if prefix or suffix:
                failed.append(el.Id)
                continue
            p.Set(number)
        elif p.StorageType == DB.StorageType.Double:
            # Prefix/suffix cannot be represented by numeric Revit parameters.
            # Preserve the existing numeric behaviour only when both are blank.
            if prefix or suffix:
                failed.append(el.Id)
                continue
            p.Set(float(number))
        else:
            failed.append(el.Id)

# ---------- 9. Report ----------
output.print_md("**Numbered {} of {} stall(s) ({}) on level '{}'.**".format(
    len(entries) - len(failed),
    len(filtered_parking),
    ", ".join(selected_types),
    selected_level_name,
))

if skipped:
    output.print_md("⚠️ Skipped {} element(s) with no location/projection: {}".format(
        len(skipped), ", ".join(str(i.IntegerValue) for i in skipped)
    ))

if failed:
    output.print_md("⚠️ Could not set '{}' on {} element(s): {}".format(
        param_name, len(failed), ", ".join(str(i.IntegerValue) for i in failed)
    ))
