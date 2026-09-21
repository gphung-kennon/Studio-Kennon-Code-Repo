# Studio Kennon QOL

A [pyRevit](https://github.com/pyrevitlabs/pyRevit) toolbar of quality-of-life
tools from Studio Kennon. Installing it adds a **Studio Kennon QOL** tab to the
Revit ribbon.

> **Status: perpetually in BETA.** Several tools change view templates or
> element parameters. Try them on a copy of your project first.

## Tools

| Panel | Tool | What it does |
| --- | --- | --- |
| Filters | [Ceiling Filter](Studio%20Kennon%20QOL.tab/Filters.panel/Ceiling%20Filter.pushbutton/README.md) | Finds each distinct ceiling *Height Offset From Level*, creates a colour-coded filter for each height, and applies them to the view templates you pick (handy for RCPs). |
| Filters | [W Filter](Studio%20Kennon%20QOL.tab/Filters.panel/W%20Filter.pushbutton/README.md) | Creates a colour-coded filter for every wall type with a Type Mark of `W1`, `W2`, `W3`... (odd numbers also get a diagonal hatch) and applies them to the view templates you pick. |
| Filters | [WT Filter](Studio%20Kennon%20QOL.tab/Filters.panel/WT%20Filter.pushbutton/README.md) | Same idea for Type Marks `WT-E##` (external, crosshatch), `WT-I##` (internal, diagonal) and `LT-##` (lining, colour only). |
| Numbering | [Number Parking](Studio%20Kennon%20QOL.tab/Numbering.panel/Number%20Parking.pushbutton/README.md) | Numbers parking stalls of the chosen type(s) on a chosen level in order along a path line you pick, with optional prefix / start number / suffix, and writes the result to a parameter (default `Carpark_Number`). |

Each tool has its own README with a full walkthrough.

## Requirements

- Revit 2024
- pyRevit 4.8.13 or later (the first release with Revit 2024 support)

## Install

You do **not** need admin rights or IT to install the tools themselves. They
are just a folder that pyRevit loads from your user profile. (pyRevit itself
must already be installed.)

### Option A: download and copy (no extra tools)

1. On GitHub, click **Code > Download ZIP** and unzip it.
2. Rename the unzipped folder to `StudioKennonQOL.extension`.
   The folder name **must end in `.extension`**, or pyRevit will ignore it.
3. Move that whole folder into `%APPDATA%\pyRevit\Extensions`
   (paste that path into the Windows Explorer address bar).
4. In Revit, go to the **pyRevit** tab and click **Reload**.

The **Studio Kennon QOL** tab should now appear.

Your `Extensions` folder should end up looking like this:

```text
%APPDATA%\pyRevit\Extensions\
├── (any other extensions, e.g. EF-Tools.extension)
└── StudioKennonQOL.extension\          <- the folder you renamed
    ├── Studio Kennon QOL.tab\
    │   ├── Filters.panel\
    │   │   ├── Ceiling Filter.pushbutton\
    │   │   ├── W Filter.pushbutton\
    │   │   └── WT Filter.pushbutton\
    │   └── Numbering.panel\
    │       └── Number Parking.pushbutton\
    ├── LICENSE
    └── README.md
```

> **Common mistake:** copying only the `Studio Kennon QOL.tab` folder into
> `Extensions`. pyRevit only loads folders ending in `.extension`, so a `.tab`
> folder sitting directly in `Extensions` is silently ignored and no tab
> appears. Always move the whole `.extension` folder.

### Option B: pyRevit CLI (easy updates)

If you have the pyRevit command line tool installed:

```text
pyrevit extend ui StudioKennonQOL https://github.com/gphung-kennon/Studio-Kennon-Code-Repo.git
```

Reload pyRevit or restart Revit afterwards. pyRevit can then update the
extension the same way it updates other extensions.

### Troubleshooting

- **No new tab:** check the folder layout matches the diagram above. In
  particular, the folder directly inside `Extensions` must be named
  `StudioKennonQOL.extension` (ends in `.extension`), and
  `Studio Kennon QOL.tab` must sit directly inside it. Then reload pyRevit
  (or restart Revit).
- **Unzipped folder has an extra layer:** some unzip tools create
  `Studio-Kennon-Code-Repo-main\Studio-Kennon-Code-Repo-main\`. Use the inner
  folder, the one that contains `Studio Kennon QOL.tab`, and rename that one.
- **Old version still showing:** replace the whole `StudioKennonQOL.extension`
  folder rather than copying files over the top, then reload.

## Repo layout

```text
Studio-Kennon-Code-Repo/            <- this repo IS the pyRevit extension
├── Studio Kennon QOL.tab/          <- becomes the ribbon tab
│   ├── Filters.panel/              <- becomes a ribbon panel
│   │   ├── Ceiling Filter.pushbutton/
│   │   ├── W Filter.pushbutton/
│   │   └── WT Filter.pushbutton/
│   └── Numbering.panel/
│       └── Number Parking.pushbutton/
├── LICENSE
└── README.md
```

Every `.pushbutton` folder contains:

| File | Purpose |
| --- | --- |
| `script.py` | The tool itself (required). |
| `bundle.yaml` | Button title and tooltip. |
| `icon.png` / `icon.dark.png` | Ribbon icon for light and dark Revit themes (96 x 96 px). |
| `README.md` | Documentation for that tool. |

## Contributing / adding a button

1. Clone the repo into a folder named `StudioKennonQOL.extension`, inside a
   folder you have registered under **Custom Extension folders** in pyRevit
   Settings:

   ```text
   git clone https://github.com/gphung-kennon/Studio-Kennon-Code-Repo.git StudioKennonQOL.extension
   ```

2. In Revit, enable **pyRevit Bundles Creator** from the pyRevit **Extensions**
   menu. Its *Create Buttons* tool scaffolds a new button and can add it to an
   existing panel or make a new one. It creates the folder and files only; you
   still write the code in `script.py`.
3. Put the new `.pushbutton` folder inside the right `.panel` folder under
   `Studio Kennon QOL.tab`.
4. Add a `bundle.yaml` (title and tooltip), an `icon.png` and `icon.dark.png`
   (96 x 96 px, matching the existing icons), and a short `README.md`.
5. Reload pyRevit to test.

## License

MIT. See [LICENSE](LICENSE).
