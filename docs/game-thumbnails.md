# Game thumbnails

Linkboy can display thumbnails next to game names, making your library easier to browse and recognize. **Linkboy does not provide or distribute thumbnail images** — you are always in control of where thumbnails come from.

## Setting a thumbnail manually

You can set a custom thumbnail for any game directly from the app:

1. **From the Game Library**
   Long-press a game and tap **Choose thumbnail** from the top-right menu.
   Then choose an image from your device to use as the game's thumbnail.

2. **From the Recents screen**
   Long-press a recently played game, then select **Set as thumbnail** from the popup menu.
   The thumbnail will be generated from the game’s most recent saved state.

Manually set thumbnails override any downloaded thumbnails for that game.

## Downloading thumbnails from your own server

Linkboy can also download thumbnails from a server URL that you provide for each system.

- The URL must end with a slash `/`, indicating it points to a directory.
- Filenames must follow the [No-Intro naming convention](https://wiki.no-intro.org/index.php?title=Naming_Convention).
- Thumbnail images must use the **`.png`** extension.

For example, if your server URL is `http://thumbnails.example.com/gba/` and a game's No-Intro name is `My Game`, Linkboy will try to download the game's thumbnail image from:  
`http://thumbnails.example.com/gba/My%20Game.png`

!!! note
    After setting URLs, you may need to rescan your games for thumbnails to appear. This only needs to be done once.

