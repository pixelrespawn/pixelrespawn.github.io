# Using Linkboy

## Import saves from the My Boy! emulator { #import-saves }

!!! note
    Only **in-game saves** (as opposed to state saves) can be shared between emulators.

1. In Linkboy, tap the **_Settings_** tab on the bottom. Scroll down, find and tap **_Open app folder_**. A file manager will show up.

2. In the file manager, click the 3-bar icon on the top-left, scroll down and tap **My Boy!**.

    !!! note
        If you can't find it, please update My Boy! to the latest version.

3. The file manager should now show the internal file structure of My Boy!. Tap the **_save_** subfolder.

4. Select all the files ending with **_.sav_** that you would like to import by tapping the icons on the left side of the file names.

    !!! tip
        * If the file names are too long and hard to read, it may be helpful to switch to list view and landscape mode.

        * You can select all files regardless of their types, but only .sav files will be recognized by Linkboy.

5. Tap the 3-dot icon on the top-right, choose **_Copy to…_**

6. Once again, click the 3-bar icon on the top-left but choose **Linkboy** this time.

7. The file manager should now show the internal file structure of Linkboy. Tap the **_saves_** subfolder.

    !!! note
        The saves folder may not have been created if you have not yet used Linkboy to play a game. In that case, you can manually create one with the file manager.

8. Tap the **_Copy_** button, which will copy all your selected files to this folder.

    !!! note
        If there are already files with the same names, they will be renamed to _.bak_ before being overwritten.

9. Now switch back to Linkboy. Start your game, tap the menu button, and then the 3-bar icon. Tap 'Reboot game'. The game will restart and your new _.sav_ file will be picked up by the emulator.


## Game thumbnails { #game-thumbnails }

Linkboy can display thumbnails next to game names, making your library easier to browse and recognize. **Linkboy does not provide or distribute thumbnail images** — you are always in control of where thumbnails come from.

### Setting a thumbnail manually

You can set a custom thumbnail for any game directly from the app:

1. **From the Game Library**
   Tap a game’s thumbnail icon, then select **Choose thumbnail** from the popup menu.
   You can pick an image file from your device to use as the new thumbnail.

2. **From the Recents screen**
   Long-press a recently played game, then select **Set as thumbnail** from the popup menu.
   The thumbnail will be generated from the game’s most recent saved state.

Manually set thumbnails override any downloaded thumbnails for that game.

### Downloading thumbnails from your own server

Linkboy can also download thumbnails from a server URL that you provide for each system.

- The URL must end with a slash `/`, indicating it points to a directory.
- Filenames must follow the [No-Intro naming convention](https://wiki.no-intro.org/index.php?title=Naming_Convention).
- Thumbnail images must use the **`.png`** extension.

For example, if your server URL is `http://thumbnails.example.com/gba/` and a game's No-Intro name is `My Game`, Linkboy will try to download the game's thumbnail image from:  
`http://thumbnails.example.com/gba/My%20Game.png`

!!! note
    After setting URLs, you may need to rescan your games for thumbnails to appear. This only needs to be done once.


## Rom patching { #rom-patching }

Linkboy supports automatic ROM patching when a game is loaded. Here's how to set it up:

!!! warning "Important"
    Your game must have been added by "**Game folders**". Otherwise, Linkboy won't have permission to locate and read your patch file.

1. Enable "Auto patch ROM" in the settings.

2. Place the **matching** patch file (.ips, .ups or .bps) in the same folder as your game file.

    !!! note
        The patch file must have the same name as the game file (excluding the extension).  
        **Example**: _your_rom.gba_ and _your_rom.ips_

3. Launch your game — it should be automatically patched.  
If it isn't and you've followed all instructions, the most likely reason is that the patch doesn't match your game or its version.
