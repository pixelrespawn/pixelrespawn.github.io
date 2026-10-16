# Creating skins

Follow these steps to create a controller skin for Linkboy. The [skin specification](skin-spec.md) describes the file formats and available options in detail.

## 1. Choose a skin type

Decide what you want to customize:

- **Control skin:** changes the appearance of controls while using an existing layout profile.
- **Full skin:** includes layouts that position the game screen, controls, and any background or overlay artwork.

Create a folder to hold your skin’s files.

## 2. Create info.json

Create a file named `info.json` in your skin folder with a unique ID and a display name. You can also include your name in the optional `author` field:

```json
{
  "id": "com.example.my_skin",
  "name": "My skin",
  "author": "Your name"
}
```

Choose an ID following the [skin identifier rules](skin-spec.md#skin-identifier), and keep it unchanged when updating the same skin. For a full skin, you will add layout entries in step 4.

## 3. Prepare your images

Create your artwork as PNG images. Use transparency where appropriate, and keep PNG file sizes as small as possible—larger files take longer to load.

Name button and D-pad images according to the [control image naming rules](skin-spec.md#control-images). For example, use `A.png` for the A button and optionally `A_pressed.png` for its pressed state.

For a full skin, you can also create backgrounds and overlays. Choose their filenames yourself; you will reference them in the layout files. See [Background and overlay images](skin-spec.md#background-and-overlay-images) for how these images are positioned and layered.

## 4. Create your layouts

**Skip this step for a control skin.**

Choose a virtual canvas size for each layout you want to provide, such as 1080 × 2400 for a portrait layout. Create a JSON file that defines both game screen rectangles (`gbaScreen` and `gbcScreen`), your controls, and any background or overlay images.

Use the [example layout](skin-spec.md#example-layout) as a starting point, and see [Layout files](skin-spec.md#layout-files) for the available fields.

If the controls are drawn into your background or overlay image, set each control’s `frame` to match the position and size of its drawing. Set its `alpha` to `0` so only the artwork is visible, while the control remains touchable.

Add your layout files to `info.json`, including each file’s virtual canvas dimensions:

```json
{
  "id": "com.example.my_skin",
  "name": "My skin",
  "author": "Your name",
  "layouts": [
    {
      "width": 1080,
      "height": 2400,
      "file": "portrait.json"
    },
    {
      "width": 2400,
      "height": 1080,
      "file": "landscape.json"
    }
  ]
}
```

Include only the layouts you have created. See [Layout entries](skin-spec.md#layout-entries) for how Linkboy selects and scales layouts for different screens.

## 5. Package your skin

Check that all referenced layouts and images are present in your skin folder. File paths are relative to this folder, which will become the archive root.

ZIP the **contents** of the folder so `info.json` is at the archive root, then rename the archive from `.zip` to `.lbskin`. See [Package format](skin-spec.md#package-format) for details.

## 6. Try it in Linkboy

[Install your skin](using-skins.md#install-a-skin) in Linkboy. For a full skin, create a layout profile from it. For a control skin, apply it to a profile that was not created from a full skin.

Try the skin in a game and adjust your artwork or layouts as needed. When testing updated full-skin layouts, create a new profile if you have edited the previous one.

## 7. Share your skin

Share the finished `.lbskin` file with users. Include a screenshot and a description of the layouts you designed it for.

Want to have your skin hosted on our website? [Contact us](contact.md).

For a complete skin to study, download **Classic purple** from the [skin gallery](skins/index.md) and extract its `.lbskin` package. If your archive tool does not recognize the extension, rename a copy to `.zip` before extracting it.
