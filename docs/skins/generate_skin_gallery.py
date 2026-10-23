#!/usr/bin/env python3
"""Generate the Linkboy skin gallery as MkDocs Markdown.

Requires Python 3.10+ and Pillow 10.1+: python -m pip install Pillow
Run from your website's skins directory:
  python generate_skin_gallery.py
Reads downloads/*.lbskin, writes previews/ and index.md.
Add skins/index.md to mkdocs.yml.
Packages remain in downloads/ and are never copied or renamed.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import quote
import zipfile

from PIL import Image, ImageDraw, ImageFont

KEY_NAMES = "Up Down Left Right A B L R Select Start TurboA TurboB TurboL TurboR Load Save FastForward SlowMotion Screenshot Menu".split()
DPAD_STATE_SUFFIXES = ["", "_u", "_d", "_l", "_r", "_ul", "_ur", "_dl", "_dr"]
MAX_ARCHIVE_MEMBER_BYTES = 64 * 1024 * 1024


def is_control_image_name(name):
    if name == "dpad":
        return True
    parts = name.split("+")
    return bool(parts) and all(p in KEY_NAMES for p in parts)


class SkinPackage:
    def __init__(self, path):
        self.path = Path(path)
        self.archive = zipfile.ZipFile(path)
        self.image_cache = {}
        self.archive_names = set(self.archive.namelist())
        try:
            self.info = self.json("info.json")
            if not isinstance(self.info.get("name"), str) or not isinstance(
                self.info.get("id"), str
            ):
                raise ValueError("info.json requires string name and id")
            self.layouts = []
            for item in self.info.get("layouts", []):
                if item["width"] <= 0 or item["height"] <= 0:
                    raise ValueError("layout dimensions must be positive")
                self.layouts.append((item, self.json(item["file"])))
        except Exception:
            self.archive.close()
            raise

    def read(self, name):
        """Read a bounded member without extracting paths onto the filesystem."""
        p = PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts or "\\" in name:
            raise ValueError(f"invalid archive-relative path: {name}")
        entry = self.archive.getinfo(name)
        if entry.file_size > MAX_ARCHIVE_MEMBER_BYTES:
            raise ValueError(f"archive member exceeds 64 MiB: {name}")
        return self.archive.read(entry)

    def json(self, name):
        return json.loads(self.read(name))

    def image(self, name):
        """Decode each PNG once and reuse it across this skin’s previews."""
        if name not in self.image_cache:
            with Image.open(io.BytesIO(self.read(name))) as image:
                image.load()
                self.image_cache[name] = image.convert("RGBA")
        return self.image_cache[name]

    def close(self):
        self.archive.close()


def draw_centered_text(draw, box, text, color="white", font_size=None):
    x, y, width, height = box
    # Pillow's bundled default font keeps the script portable.
    font = (
        ImageFont.load_default(size=font_size)
        if font_size
        else ImageFont.load_default()
    )
    bounds = draw.textbbox((0, 0), text, font=font)
    draw.text(
        (
            x + (width - (bounds[2] - bounds[0])) / 2 - bounds[0],
            y + (height - (bounds[3] - bounds[1])) / 2 - bounds[1],
        ),
        text,
        font=font,
        fill=color,
    )


def control_image_stem(control_input):
    if control_input.get("type", "button") == "dpad":
        return "dpad"
    keys = control_input["key"]
    keys = [keys] if isinstance(keys, str) else keys
    if not keys or any(k not in KEY_NAMES for k in keys):
        raise ValueError(f"invalid button keys: {keys}")
    return "+".join(k for k in KEY_NAMES if k in keys)


# Shared control-skin layouts supplied by the Linkboy developer.
CONTROL_PORTRAIT_LAYOUT = {
    "gbaScreen": {"x": 0, "y": 366, "width": 1080, "height": 720},
    "gbcScreen": {"x": 0, "y": 350, "width": 1080, "height": 972},
    "controls": [
        {
            "input": {"type": "dpad"},
            "frame": {"x": 48, "y": 1672, "width": 439, "height": 439},
        },
        {
            "input": {"type": "button", "key": ["A"]},
            "frame": {"x": 860, "y": 1940, "width": 171, "height": 171},
        },
        {
            "input": {"type": "button", "key": ["B"]},
            "frame": {"x": 665, "y": 1867, "width": 171, "height": 171},
        },
        {
            "input": {"type": "button", "key": ["L"]},
            "frame": {"x": 48, "y": 1380, "width": 244, "height": 122},
        },
        {
            "input": {"type": "button", "key": ["R"]},
            "frame": {"x": 787, "y": 1380, "width": 244, "height": 122},
        },
        {
            "input": {"type": "button", "key": ["Select"]},
            "frame": {"x": 738, "y": 1672, "width": 134, "height": 61},
        },
        {
            "input": {"type": "button", "key": ["Start"]},
            "frame": {"x": 897, "y": 1672, "width": 134, "height": 61},
        },
        {
            "input": {"type": "button", "key": ["Menu"]},
            "frame": {"x": 909, "y": 48, "width": 122, "height": 122},
        },
        {
            "input": {"type": "button", "key": ["FastForward"]},
            "frame": {"x": 48, "y": 48, "width": 122, "height": 122},
        },
    ],
}

CONTROL_LANDSCAPE_LAYOUT = {
    "gbaScreen": {"x": 390, "y": 0, "width": 1621, "height": 1080},
    "gbcScreen": {"x": 601, "y": 0, "width": 1201, "height": 1080},
    "controls": [
        {
            "input": {"type": "dpad"},
            "frame": {"x": 48, "y": 592, "width": 439, "height": 439},
        },
        {
            "input": {"type": "button", "key": ["A"]},
            "frame": {"x": 2184, "y": 860, "width": 171, "height": 171},
        },
        {
            "input": {"type": "button", "key": ["B"]},
            "frame": {"x": 1989, "y": 787, "width": 171, "height": 171},
        },
        {
            "input": {"type": "button", "key": ["L"]},
            "frame": {"x": 48, "y": 300, "width": 244, "height": 121},
        },
        {
            "input": {"type": "button", "key": ["R"]},
            "frame": {"x": 2111, "y": 300, "width": 244, "height": 121},
        },
        {
            "input": {"type": "button", "key": ["Select"]},
            "frame": {"x": 1307, "y": 970, "width": 134, "height": 61},
        },
        {
            "input": {"type": "button", "key": ["Start"]},
            "frame": {"x": 1465, "y": 970, "width": 134, "height": 61},
        },
        {
            "input": {"type": "button", "key": ["Menu"]},
            "frame": {"x": 2233, "y": 48, "width": 122, "height": 122},
        },
        {
            "input": {"type": "button", "key": ["FastForward"]},
            "frame": {"x": 48, "y": 48, "width": 122, "height": 122},
        },
    ],
}


def get_control_skin_layout(width, height):
    if height > width:
        return {"width": 1080, "height": 2404}, CONTROL_PORTRAIT_LAYOUT
    return {"width": 2404, "height": 1080}, CONTROL_LANDSCAPE_LAYOUT


def choose_layout(layouts, width, height, near_aspect):
    """Prefer aspect ratio, then canvas resolution among near-equal ratios.

    Opposite orientations are excluded. Square layouts remain eligible for both
    orientations. There is intentionally no upper aspect-ratio cutoff.
    """
    candidates = []
    for canvas, layout in layouts:
        layout_width, layout_height = canvas["width"], canvas["height"]
        same_orientation = (
            layout_width == layout_height
            or width == height
            or (layout_width > layout_height) == (width > height)
        )
        difference = abs(math.log((layout_width / layout_height) / (width / height)))
        distance = math.hypot(
            math.log(layout_width / width), math.log(layout_height / height)
        )
        candidate = (difference, distance, canvas, layout)
        if same_orientation:
            candidates.append(candidate)
    if not candidates:
        return None
    best = min(c[0] for c in candidates)
    return min(
        (c for c in candidates if c[0] <= best + math.log1p(near_aspect)),
        key=lambda c: (c[1], c[0]),
    )[2:]


def render_layout_preview(skin, canvas, layout, target, max_edge, default):
    """Fit and center the canvas, then draw backgrounds, screen, overlays, controls."""
    width, height = target
    ratio = min(1, max_edge / max(width, height))
    preview = Image.new(
        "RGBA", (round(width * ratio), round(height * ratio)), "#20212a"
    )
    preview_width, preview_height = preview.size
    scale = min(preview_width / canvas["width"], preview_height / canvas["height"])
    offset_x, offset_y = (preview_width - canvas["width"] * scale) / 2, (
        preview_height - canvas["height"] * scale
    ) / 2
    placeholders = set()

    def box(frame):
        return (
            round(offset_x + frame["x"] * scale),
            round(offset_y + frame["y"] * scale),
            max(1, round(frame["width"] * scale)),
            max(1, round(frame["height"] * scale)),
        )

    def paste(image, frame, alpha=1):
        x, y, image_width, image_height = box(frame)
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between 0 and 1")
        image = image.resize((image_width, image_height), Image.Resampling.LANCZOS)
        if alpha != 1:
            image.putalpha(image.getchannel("A").point(lambda a: round(a * alpha)))
        preview.alpha_composite(image, (x, y))

    for layer in layout.get("backgrounds", []):
        paste(skin.image(layer["file"]), layer["frame"], layer.get("alpha", 1))
    screen_key = "gbaScreen" if width > height else "gbcScreen"
    x, y, screen_width, screen_height = box(layout[screen_key])
    draw = ImageDraw.Draw(preview)
    # Subtle checkerboard distinguishes the game screen without competing with artwork.
    tile = max(4, round(min(screen_width, screen_height) / 12))
    for row, top in enumerate(range(y, y + screen_height, tile)):
        for col, left in enumerate(range(x, x + screen_width, tile)):
            color = "#303030" if (row + col) % 2 == 0 else "#3b3b3b"
            draw.rectangle(
                (
                    left,
                    top,
                    min(left + tile, x + screen_width) - 1,
                    min(top + tile, y + screen_height) - 1,
                ),
                fill=color,
            )
    for layer in layout.get("overlays", []):
        paste(skin.image(layer["file"]), layer["frame"], layer.get("alpha", 1))
    for control in layout.get("controls", []):
        if control.get("alpha", 1) == 0:
            continue
        name = control_image_stem(control["input"])
        file = name + ".png"
        source = (
            skin
            if file in skin.archive_names
            else default if default and file in default.archive_names else None
        )
        if source:
            image = source.image(file)
        else:
            placeholders.add(name)
            image = Image.new("RGBA", (240, 240))
            draw = ImageDraw.Draw(image)
            if name == "dpad":
                draw.rectangle((80, 10, 160, 230), fill="#555d70")
                draw.rectangle((10, 80, 230, 160), fill="#555d70")
            else:
                draw.ellipse((8, 8, 232, 232), fill="#555d70")
                draw_centered_text(draw, (0, 0, 240, 240), name)
        paste(image, control["frame"], control.get("alpha", 1))
    return preview.convert("RGB"), placeholders


def render_control_grid(skin):
    files = []
    for name in sorted(skin.archive_names):
        if "/" in name or not name.endswith(".png"):
            continue
        stem = name[:-4]
        base = stem.removesuffix("_pressed")
        if is_control_image_name(base) or stem in [
            "dpad" + s for s in DPAD_STATE_SUFFIXES
        ]:
            files.append(name)
    if not files:
        return None
    columns = min(5, len(files))
    cell = 180
    preview = Image.new(
        "RGB", (columns * cell, math.ceil(len(files) / columns) * cell), "#20212a"
    )
    draw = ImageDraw.Draw(preview)
    for i, name in enumerate(files):
        x, y = i % columns * cell, i // columns * cell
        image = skin.image(name).copy()
        image.thumbnail((140, 125), Image.Resampling.LANCZOS)
        preview.paste(
            image,
            (x + (cell - image.width) // 2, y + 8 + (125 - image.height) // 2),
            image,
        )
        draw_centered_text(draw, (x, y + 140, cell, 24), name, "#e4e7ef")
    return preview


# Gallery cards and enlarged preview viewer.
CSS = """
.skin-gallery {
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));
    gap:24px;
}

.skin-card {
    border:1px solid #8885;
    border-radius:12px;
    padding:18px;
    min-width:0;
}

.skin-card h3 {
    margin:12px 0 4px;
}

.skin-main {
    display:block;
    background:#20212a;
    border-radius:8px;
    text-align:center;
}

.skin-main img {
    width:100%;
    height:320px;
    object-fit:contain;
    display:block;
}

.skin-thumbs {
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    margin:12px 0;
}

.skin-thumbs button {
    background:transparent;
    border:1px solid #8888;
    border-radius:5px;
    padding:4px;
    cursor:pointer;
    color:inherit;
}

.skin-thumbs button[aria-pressed=true] {
    outline:2px solid #8874dd;
}

.skin-thumbs img {
    width:54px;
    height:54px;
    object-fit:contain;
    display:block;
}

.skin-download {
    display:inline-block;
    padding:9px 16px;
    background:#6651b4;
    color:white!important;
    border-radius:6px;
    text-decoration:none;
}

.skin-note {
    font-size:.85em;
    opacity:.8;
}

.skin-caption {
    font-size:.9em;
}

.skin-viewer {
    border:0;
    border-radius:12px;
    padding:0;
    background:#20212a;
    color:#fff;
    width:min(1100px,94vw);
    max-width:94vw;
    max-height:94vh;
    box-sizing:border-box;
}

.skin-viewer::backdrop {
    background:#000c;
}

.skin-viewer-stage {
    position:relative;
}

.skin-viewer img {
    display:block;
    width:100%;
    height:80vh;
    max-height:calc(94vh - 64px);
    object-fit:contain;
}

.skin-viewer button {
    position:absolute;
    z-index:1;
    cursor:pointer;
    border:1px solid #ffffff55;
    background:#18181899;
    color:white;
    border-radius:50%;
    width:48px;
    height:48px;
    padding:0;
    font:32px/1 system-ui;
    display:flex;
    align-items:center;
    justify-content:center;
    transition:background .15s;
}

.skin-viewer button:hover {
    background:#181818dd;
}

.skin-viewer button:focus-visible {
    outline:3px solid white;
    outline-offset:2px;
}

.skin-viewer button:disabled {
    display:none;
}

.skin-viewer [data-action=prev] {
    left:12px;
    top:50%;
    transform:translateY(-50%);
}

.skin-viewer [data-action=next] {
    right:12px;
    top:50%;
    transform:translateY(-50%);
}

.skin-viewer [data-action=close] {
    top:12px;
    right:12px;
}

.skin-viewer-caption {
    text-align:center;
    margin:0;
    padding:12px 16px;
    font-size:14px;
}
"""

JS = r"""(() => {
  const viewer = document.createElement('dialog');
  viewer.className = 'skin-viewer';
  viewer.setAttribute('aria-label', 'Skin preview');
  viewer.innerHTML = `
    <div class="skin-viewer-stage">
      <img alt="">
      <button type="button" data-action="prev" aria-label="Previous preview">&#8592;</button>
      <button type="button" data-action="next" aria-label="Next preview">&#8594;</button>
      <button type="button" data-action="close" aria-label="Close preview">&times;</button>
    </div>
    <p class="skin-viewer-caption" aria-live="polite"></p>
  `;
  document.body.appendChild(viewer);
  let previews = [], index = 0, opener = null, skinName = '';
  const show = () => {
    const b = previews[index];
    viewer.querySelector('img').src = b.dataset.src;
    viewer.querySelector('img').alt = skinName + ': ' + b.dataset.label;
    viewer.querySelector('.skin-viewer-caption').textContent = skinName + ' — ' + b.dataset.label + ' (' + (index + 1) + '/' + previews.length + ')';
    viewer.querySelector('[data-action="prev"]').disabled = previews.length < 2;
    viewer.querySelector('[data-action="next"]').disabled = previews.length < 2;
  };
  // Wrap around when navigating past either end of this skin's previews.
  const move = delta => {
    index = (index + delta + previews.length) % previews.length;
    show();
  };
  viewer.querySelector('[data-action="prev"]').addEventListener('click', () => move(-1));
  viewer.querySelector('[data-action="next"]').addEventListener('click', () => move(1));
  viewer.querySelector('[data-action="close"]').addEventListener('click', () => viewer.close());
  viewer.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault();
      move(e.key === 'ArrowLeft' ? -1 : 1);
    }
  });
  viewer.addEventListener('close', () => { if (opener) opener.focus(); });
  viewer.addEventListener('click', e => {
    const r = viewer.getBoundingClientRect();
    if (e.target === viewer && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) viewer.close();
  });
  document.querySelectorAll('.skin-card').forEach(card => {
    const link = card.querySelector('.skin-main');
    if (!link) return;
    const buttons = Array.from(card.querySelectorAll('.skin-thumbs button'));
    buttons.forEach(b => b.addEventListener('click', () => {
      link.querySelector('img').src = b.dataset.src;
      link.querySelector('img').alt = b.dataset.label;
      link.href = b.dataset.src;
      card.querySelector('.skin-caption').textContent = b.dataset.label;
      buttons.forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    }));
    link.addEventListener('click', e => {
      e.preventDefault();
      previews = buttons;
      index = Math.max(0, buttons.findIndex(b => b.getAttribute('aria-pressed') === 'true'));
      opener = link;
      skinName = card.querySelector('h3').textContent;
      show();
      viewer.showModal();
    });
  });
})();"""


def parse_screen_size(value):
    try:
        width, height = map(int, value.lower().split("x"))
        if not 1 <= width <= height <= 10000:
            raise ValueError()
        return width, height
    except ValueError:
        raise argparse.ArgumentTypeError(
            "use portrait WIDTHxHEIGHT, e.g. 1080x2400 (maximum 10000)"
        )


def generate_previews(skin, output, args, default):
    """Render supported orientations; control skins also receive an asset grid."""
    path = skin.path
    slug = re.sub("[^a-zA-Z0-9_-]+", "-", path.stem).strip("-") or "skin"
    slug += "-" + hashlib.sha256(path.name.encode()).hexdigest()[:8]
    previews = []
    missing = set()
    targets = [("Phone", args.phone)] + (
        [("Tablet", args.tablet)] if skin.layouts else []
    )
    for device, (portrait_width, portrait_height) in targets:
        for orientation, (width, height) in [
            ("portrait", (portrait_width, portrait_height)),
            ("landscape", (portrait_height, portrait_width)),
        ]:
            selection = (
                choose_layout(skin.layouts, width, height, args.near_aspect)
                if skin.layouts
                else get_control_skin_layout(width, height)
            )
            if selection is None:
                continue
            image, placeholders = render_layout_preview(
                skin, *selection, (width, height), args.max_edge, default
            )
            missing.update(placeholders)
            filename = f"previews/{slug}-{device.lower()}-{orientation}.png"
            image.save(output / filename, optimize=True)
            previews.append((filename, f"{device} · {orientation}"))
    if not skin.layouts:
        grid = render_control_grid(skin)
        if grid:
            filename = f"previews/{slug}-controls.png"
            grid.save(output / filename, optimize=True)
            previews.append((filename, "Included controls and states"))
    return previews, missing


def build_skin_card(skin, previews, missing):
    """Escape package metadata before placing it in the gallery markup."""
    path = skin.path
    download = "downloads/" + quote(path.name, safe="")

    def escape_html(value):
        return html.escape(str(value), quote=True)

    name = escape_html(skin.info["name"])
    author = skin.info.get("author")
    card = '<article class="skin-card">'
    if previews:
        first, label = previews[0]
        card += (
            f'<a class="skin-main" href="{first}">'
            f'<img loading="lazy" src="{first}" alt="{escape_html(label)}">'
            "</a>"
            f'<p class="skin-caption">{escape_html(label)}</p>'
            '<div class="skin-thumbs">'
        )
        for i, (src, label) in enumerate(previews):
            selected = str(i == 0).lower()
            card += (
                f'<button type="button" data-src="{src}" '
                f'data-label="{escape_html(label)}" '
                f'aria-label="Show {escape_html(label)}" aria-pressed="{selected}">'
                f'<img loading="lazy" src="{src}" alt="">'
                "</button>"
            )
        card += "</div>"
    else:
        card += "<p>No matching preview for the configured phone and tablet sizes.</p>"
    card += f"<h3>{name}</h3>"
    if author:
        card += f"<p>By {escape_html(author)}</p>"
    if missing:
        card += '<p class="skin-note">Unavailable default controls are shown with generic placeholders.</p>'
        print(
            f'{path.name}: placeholder controls: {", ".join(sorted(missing))}',
            file=sys.stderr,
        )
    card += (
        f'<a class="skin-download" href="{download}" download>Download</a></article>'
    )
    return card


def write_gallery_page(output, groups, guide_url):
    """Write a single MkDocs page with its gallery styles and viewer script."""
    content = (
        '<h1>Download skins</h1><p>Give Linkboy a new look with custom controller skins. Download a skin below, then see <a href="'
        + html.escape(guide_url, quote=True)
        + '">Using skins</a> for installation and setup instructions.</p>'
    )
    for group, cards in groups.items():
        if cards:
            content += (
                f'<h2>{group}</h2><div class="skin-gallery">'
                + "".join(cards)
                + "</div>"
            )
    content += '<p>Want to share your skin? <a href="../contact/">Contact us</a> to have it hosted on our website.</p>'
    (output / "index.md").write_text(
        "---\ntitle: Download skins\n---\n\n<style>\n"
        + CSS
        + "\n</style>\n\n"
        + content
        + "\n\n<script>\n"
        + JS
        + "\n</script>\n",
        encoding="utf-8",
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--phone",
        type=parse_screen_size,
        default=(1080, 2400),
        metavar="WIDTHxHEIGHT",
        help="phone size in portrait order (default: 1080x2400)",
    )
    parser.add_argument(
        "--tablet",
        type=parse_screen_size,
        default=(1600, 2560),
        metavar="WIDTHxHEIGHT",
        help="tablet size in portrait order (default: 1600x2560)",
    )
    parser.add_argument(
        "--near-aspect",
        type=float,
        default=0.01,
        help="near-equal aspect ratio band for resolution tie-break (default .01)",
    )
    parser.add_argument(
        "--max-edge", type=int, default=960, help="preview maximum edge in pixels"
    )
    parser.add_argument(
        "--default-skin",
        type=Path,
        help="package containing default control PNGs for accurate fallback",
    )
    parser.add_argument(
        "--guide-url",
        default="../using-skins/",
        help="installation guide link relative to generated page",
    )
    args = parser.parse_args()
    if not 0 <= args.near_aspect <= 1 or not 128 <= args.max_edge <= 4096:
        parser.error("near-aspect must be 0..1 and max-edge 128..4096")
    return parser, args


def main():
    parser, args = parse_arguments()
    output = Path.cwd()
    downloads = output / "downloads"
    if not downloads.is_dir():
        parser.error(
            "downloads/ subdirectory does not exist; run from your skins directory"
        )
    paths = sorted(
        p for p in downloads.iterdir() if p.is_file() and p.suffix.lower() == ".lbskin"
    )
    if not paths:
        parser.error("no .lbskin files found in downloads/")
    (output / "previews").mkdir(exist_ok=True)
    default = SkinPackage(args.default_skin) if args.default_skin else None
    groups = {"Full skins": [], "Control skins": []}
    errors = 0
    try:
        for path in paths:
            skin = None
            try:
                skin = SkinPackage(path)
                previews, missing = generate_previews(skin, output, args, default)
                card = build_skin_card(skin, previews, missing)
                groups["Full skins" if skin.layouts else "Control skins"].append(card)
                print(f"{path.name}: {len(previews)} previews")
            except Exception as e:
                errors += 1
                print(f"ERROR {path.name}: {e}", file=sys.stderr)
            finally:
                if skin:
                    skin.close()
    finally:
        if default:
            default.close()
    write_gallery_page(output, groups, args.guide_url)
    if errors:
        print(f"{errors} package(s) failed; see errors above.", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
