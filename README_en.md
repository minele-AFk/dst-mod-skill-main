# DST Mod Development Toolkit

[中文说明](./README.md)

This is a Skill for assisting with Don't Starve Together mod development.

## Requirements

- Don't Starve Together
- Don't Starve Mod Tools, when a task uses the official asset compiler. If it is missing, explain the source and installation steps first; get the user's explicit authorization before launching Steam or an installer.
- Python 3.10 or newer for the current project tools.
- AI tools that support Skills, such as Codex, Claude Code, and OpenCode

Common game directories:

- Windows: `C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Windows: `D:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together`
- Windows: `E:\SteamLibrary\steamapps\common\Don't Starve Together`
- Linux: `~/.local/share/Steam/steamapps/common/Don't Starve Together`
- macOS: `~/Library/Application Support/Steam/steamapps/common/Don't Starve Together`

Common bundle paths:

- Script bundle: `data/databundles/scripts.zip`
- Image bundle: `data/databundles/images.zip`

If the game is installed outside the common directories, provide its actual path when invoking the Skill.
