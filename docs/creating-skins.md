# Creating skins

Start with an existing skin, customize its artwork and layouts, then package it for use in Linkboy. For detailed file formats and rules, see the [skin specification](skin-spec.md).

## Start with an example

[Download Classic purple](downloads/classic_purple.lbskin){ .md-button download="classic_purple.lbskin" }

Extract the `.lbskin` package into a folder to use it as a starting point. If your archive tool does not recognize the extension, rename a copy from `.lbskin` to `.zip` before extracting it.

The example contains PNG images and eight layouts for different portrait and landscape screen shapes.

## 1. Name your skin

Edit `info.json` and give your skin a unique `id` and a display `name`. For example, change these two fields to:

```json
"id": "com.example.my_skin",
"name": "My skin"
```

Keep the identifier stable when updating the same skin. See [Skin identifier](skin-spec.md#skin-identifier) for the naming rules.

If you are making a control skin, remove the `layouts` entry and any unused layout and background files from your working folder.

## 2. Prepare the artwork

Create or edit your artwork as PNG images. Use transparency around controls where appropriate. Keep PNG file sizes as small as possible, as larger files take longer to load.

Replace the example’s images with your own artwork. Use the [control image naming reference](skin-spec.md#control-images) when adding or replacing button and D-pad images.

For backgrounds and overlays, update the image paths in your layout files to point to your artwork. See [Background and overlay images](skin-spec.md#background-and-overlay-images) for placement and drawing order.

## 3. Adjust the layouts

Skip this step for a control skin.

For a full skin, edit the layout files to position the game screens and touch controls over your artwork. Start with the example layout closest to your intended screen shape, then adapt the others as needed.

For example, this places an A button in the layout:

```json
{
  "input": { "key": "A" },
  "frame": { "x": 878, "y": 1688, "width": 164, "height": 164 }
}
```

If your background or overlay already includes the button artwork, set the corresponding control’s `alpha` to `0`. Its touch area remains active while its separate image is hidden.

Update the `layouts` entries in `info.json` to match the layout files you include. See [Layout entries](skin-spec.md#layout-entries) for virtual canvas dimensions and layout selection, and [Layout files](skin-spec.md#layout-files) for the available fields.

## 4. Package your skin

1. Gather `info.json` and the layouts and images your skin uses in a staging folder, keeping any referenced subdirectories.
2. Check that all referenced file paths match the packaged files, following the [package format](skin-spec.md#package-format).
3. ZIP the **contents** of the folder so `info.json` is at the archive root. Do not ZIP the enclosing folder itself.
4. Rename the resulting archive from `.zip` to `.lbskin`.

## 5. Test and share

[Install your skin](using-skins.md#install-a-skin) in Linkboy. For a full skin, create a layout profile from it to test your layouts. For a control skin, apply it to a profile that was not created from a full skin.


Share the finished `.lbskin` file with users. Include a screenshot and a description of the layouts you designed it for.

Want to share your skin? Contact us to have it hosted on our website.
