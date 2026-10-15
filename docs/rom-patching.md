# ROM patching

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

