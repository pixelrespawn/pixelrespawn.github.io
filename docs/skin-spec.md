# Skin specification

This reference describes the file structure and JSON format used to create controller skins for Linkboy.

## Package format

A Linkboy skin package is a ZIP archive with a filename ending in `.lbskin`. The archive must contain `info.json` at its root.

Any file referenced in `info.json` or a layout JSON file can use a path relative to the **archive root**. For example, you can place layout files in `layouts/` and background or overlay images in `images/`, then reference them as `layouts/portrait.json` and `images/background.png`. Paths are always relative to the archive root, even when the referring layout file is in a subdirectory.

Control images are looked up by the naming convention described under [Control images](#control-images), rather than by a `file` field.

| Example file | Purpose |
| --- | --- |
| `info.json` | Skin identifier, display name, and layout entries |
| `layout-1080x2400.json` | A layout for a reference canvas of 1080 × 2400 |
| `background-1080x2400.png` | Artwork referenced by a layout |
| `A.png` | Base image for the A button |
| `A_pressed.png` | Optional pressed image for the A button |
| `dpad.png` | Base image for the D-pad |
| `dpad_u.png` | Optional image for the up direction |

Use valid JSON with quoted property names and no comments or trailing commas. Match the capitalization shown for input names and control filenames.

## Skin metadata: info.json

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | String | Yes | Unique skin identifier, for example `com.example.skins.my_skin` |
| `name` | String | Yes | Display name shown to users |
| `author` | String | No | Creator's name |
| `layouts` | Array of layout entries | No | Defaults to `[]` |

### Skin identifier

The skin ID must start with a letter or digit and may contain only ASCII letters (`A–Z`, `a–z`), digits (`0–9`), dots (`.`), underscores (`_`), and hyphens (`-`).

We recommend a fully qualified reverse-domain-style identifier, such as `com.example.skins.my_skin`, to help avoid conflicts with other skins. Keep the identifier stable when updating the same skin.

### Layout entries

Each layout entry contains:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `width` | Integer | Yes | Virtual canvas width |
| `height` | Integer | Yes | Virtual canvas height |
| `file` | String | Yes | Layout JSON path relative to the archive root |

```json
{
  "id": "linkboy.skins.classic_purple",
  "name": "Classic purple",
  "author": "Pixel Respawn",
  "layouts": [
    { "width": 1080, "height": 2400, "file": "layout-1080x2400.json" },
    { "width": 2400, "height": 1080, "file": "layout-2400x1080.json" }
  ]
}
```

The `width` and `height` define a **virtual canvas**. All coordinates and sizes in that layout JSON file relate to this canvas. Linkboy converts them to real screen coordinates at runtime; the canvas dimensions do not have to match the device’s screen resolution.

Linkboy chooses the best layout according to the screen’s aspect ratio and resolution. When two layouts have very close aspect ratios, it chooses the layout whose canvas size is closest to the screen resolution.

If the chosen layout’s virtual canvas size differs from the screen size, Linkboy scales the layout to fit the screen while preserving its aspect ratio, then centers it on the screen.

A control skin can omit `layouts`:

```json
{
  "id": "com.example.skins.my_controls",
  "name": "My controls",
  "author": "Example Studio"
}
```

## Layout files

| Field | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `gbaScreen` | Rectangle | Yes | — | GBA game screen placement |
| `gbcScreen` | Rectangle | Yes | — | GB/GBC game screen placement |
| `controls` | Array of controls | No | `[]` | Touch controls |
| `backgrounds` | Array of images | No | `[]` | Background artwork |
| `overlays` | Array of images | No | `[]` | Overlay artwork |

### Rectangles

All rectangles use the following four required integer fields. Coordinates are measured from the top-left of the layout’s virtual canvas: x increases to the right and y increases downward.

| Field | Meaning |
| --- | --- |
| `x` | Left position |
| `y` | Top position |
| `width` | Rectangle width |
| `height` | Rectangle height |

```json
{ "x": 0, "y": 286, "width": 1080, "height": 720 }
```

### Controls

| Field | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `input` | Input object | Yes | — | D-pad or button mapping |
| `frame` | Rectangle | Yes | — | Control position and size |
| `alpha` | Number from 0 to 1 | No | `1` | Control image opacity |

`alpha` is inclusive of both endpoints: `0` is invisible, `1` is fully opaque, and values between them are partially transparent. **An invisible control remains touchable.** Set `alpha` to `0` when the control artwork is already drawn into a background or overlay.

### Button input

| Field | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `type` | String | No | `"button"` | Button input type |
| `key` | Key name or array of key names | Yes | — | Input or combined inputs |

If `type` is omitted, it defaults to `"button"`:

```json
{ "key": "A" }
```

You can also specify `"type": "button"` explicitly. A single key can use either form:

```json
{ "type": "button", "key": "A" }
```

```json
{ "type": "button", "key": ["A"] }
```

Multiple keys combine their inputs:

```json
{ "type": "button", "key": ["A", "B"] }
```

#### Supported keys

Key names are case-sensitive. The table below lists them in declaration order, which also determines the filename order for combined inputs. Read each row from left to right, then continue to the next row.

| Category | Names |
| --- | --- |
| Directional | `Up`, `Down`, `Left`, `Right` |
| Console | `A`, `B`, `L`, `R`, `Select`, `Start` |
| Turbo | `TurboA`, `TurboB`, `TurboL`, `TurboR` |
| Save states | `Load`, `Save` |
| Speed | `FastForward`, `SlowMotion` |
| Other actions | `Screenshot`, `Menu` |

### D-pad input

For a standard D-pad, use:

```json
{ "type": "dpad" }
```

The `up`, `down`, `left`, and `right` fields define the input for each D-pad direction. Each accepts a single key name from [Supported keys](#supported-keys), such as `"Up"` or `"A"`. Arrays are not supported. All four fields are optional; omit them to use the standard directional inputs.

| Field | Default |
| --- | --- |
| `up` | `"Up"` |
| `down` | `"Down"` |
| `left` | `"Left"` |
| `right` | `"Right"` |

### Background and overlay images

Images and controls are displayed in this order, from back to front:

1. Background images (`backgrounds`).
2. The game screen.
3. Overlay images (`overlays`).
4. All controls.

Both `backgrounds` and `overlays` contain image objects:

| Field | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `frame` | Rectangle | Yes | — | Image position and size |
| `file` | String | Yes | — | Image path relative to the archive root |
| `alpha` | Number from 0 to 1 | No | `1` | Image opacity |

```json
{
  "frame": { "x": 0, "y": 0, "width": 1080, "height": 2400 },
  "file": "images/background.png",
  "alpha": 1
}
```

### Example layout

This abbreviated example illustrates the structure. The Classic purple skin includes complete layouts with all console controls.

```json
{
  "gbaScreen": { "x": 0, "y": 286, "width": 1080, "height": 720 },
  "gbcScreen": { "x": 0, "y": 160, "width": 1080, "height": 972 },
  "backgrounds": [
    {
      "frame": { "x": 0, "y": 0, "width": 1080, "height": 2400 },
      "file": "background-1080x2400.png"
    }
  ],
  "controls": [
    {
      "input": { "type": "dpad" },
      "frame": { "x": 40, "y": 1580, "width": 440, "height": 440 }
    },
    {
      "input": { "type": "button", "key": "A" },
      "frame": { "x": 878, "y": 1688, "width": 164, "height": 164 }
    },
    {
      "input": { "type": "button", "key": "B" },
      "frame": { "x": 658, "y": 1748, "width": 164, "height": 164 }
    }
  ]
}
```

## Control images

Linkboy looks up control images by filename; individual controls do not have an image filename field.

### Buttons

Use the key name for the base image and append `_pressed` for the optional pressed image.

For combined inputs, Linkboy joins the key names with `+` in the declaration order shown in [Supported keys](#supported-keys), regardless of their order in the JSON array. For example, a button combining A, B, Select, and Start uses `A+B+Select+Start.png` and optionally `A+B+Select+Start_pressed.png`.

| Control | Base image | Optional pressed image |
| --- | --- | --- |
| A | `A.png` | `A_pressed.png` |
| B | `B.png` | `B_pressed.png` |
| L / R | `L.png` / `R.png` | `L_pressed.png` / `R_pressed.png` |
| Select / Start | `Select.png` / `Start.png` | `Select_pressed.png` / `Start_pressed.png` |
| Turbo A | `TurboA.png` | `TurboA_pressed.png` |
| Turbo B | `TurboB.png` | `TurboB_pressed.png` |
| Turbo L | `TurboL.png` | `TurboL_pressed.png` |
| Turbo R | `TurboR.png` | `TurboR_pressed.png` |
| Load state | `Load.png` | `Load_pressed.png` |
| Save state | `Save.png` | `Save_pressed.png` |
| Fast-forward | `FastForward.png` | `FastForward_pressed.png` |
| Slow motion | `SlowMotion.png` | `SlowMotion_pressed.png` |
| Screenshot | `Screenshot.png` | `Screenshot_pressed.png` |
| Menu | `Menu.png` | `Menu_pressed.png` |
| A+B | `A+B.png` | `A+B_pressed.png` |

If a button’s pressed image is omitted, its base image is used in both states.

### D-pad

| State | Filename |
| --- | --- |
| Neutral / base | `dpad.png` |
| Up | `dpad_u.png` |
| Down | `dpad_d.png` |
| Left | `dpad_l.png` |
| Right | `dpad_r.png` |
| Up-left | `dpad_ul.png` |
| Up-right | `dpad_ur.png` |
| Down-left | `dpad_dl.png` |
| Down-right | `dpad_dr.png` |

All directional images are optional. Any missing directional image uses `dpad.png`. Supply only `dpad.png` for a static D-pad.

### Default skin fallback

If a control’s base image is absent, Linkboy uses the default skin’s image for that control. This lets a skin replace selected controls without supplying a complete image set.

If the base image is present but a pressed or directional image is absent, the supplied base image is used for that state.

## Invalid controls

Controls that fail deserialization, such as a button with an unknown key name or a control missing a required rectangle field, are skipped individually. If a control does not appear, check its JSON and key spelling. This does not mean a malformed JSON document or an invalid top-level layout can be loaded.
