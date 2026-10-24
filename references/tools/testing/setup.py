#!/usr/bin/env python3
"""Install dst_test_mod into a downloaded DST dedicated server.

The game server (~4 GB) and steamcmd are intentionally NOT part of this
repository; download them first (see README.md), then run:

    python3 tools/setup.py

This script:
  1. copies mods/dst_test_mod into <game>/Contents/mods/dst_test_mod
  2. appends ForceEnableMod("dst_test_mod") to modsettings.lua (idempotent)
  3. ensures pause_when_empty = false in Cluster/cluster.ini (idempotent)
"""

import argparse
import shutil
import sys
from pathlib import Path

import game_config as cfg
import game_process as gp

MOD_SOURCE = cfg.ROOT / "mods" / cfg.MOD_NAME


def find_game_dir(explicit):
    if explicit:
        return Path(explicit).expanduser().resolve()
    return cfg.SERVER_DIR


def find_mods_dir(game_dir):
    """Locate the game's mods directory (macOS servers live in a .app)."""
    candidates = [
        game_dir / "Contents" / "mods",
        game_dir / "dontstarve_dedicated_server_nullrenderer.app" / "Contents" / "mods",
    ]
    candidates += [app / "Contents" / "mods" for app in game_dir.glob("*.app")]
    for mods_dir in candidates:
        if (mods_dir / "dedicated_server_mods_setup.lua").exists():
            return mods_dir
    return None


def install_mod(mods_dir):
    if mods_dir is None:
        raise SystemExit(
            "game mods directory not found\n"
            "Make sure the DST dedicated server is downloaded there first "
            "(see README.md)."
        )

    dest = mods_dir / cfg.MOD_NAME
    shutil.copytree(MOD_SOURCE, dest, dirs_exist_ok=True)
    print(f"installed {cfg.MOD_NAME} -> {dest}")

    settings = mods_dir / "modsettings.lua"
    text = settings.read_text(encoding="utf-8")
    marker = f'ForceEnableMod("{cfg.MOD_NAME}")'
    if marker not in text:
        text += "\n-- Force-load the local test mod (added by tools/setup.py)\n"
        text += marker + "\n"
        settings.write_text(text, encoding="utf-8")
        print(f"patched {settings}")
    else:
        print(f"{settings} already force-enables {cfg.MOD_NAME}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-dir",
        help="path to the downloaded DST dedicated server "
        "(default: <repo>/dontstarvetogether_dedicated_server)",
    )
    parser.add_argument(
        "--no-pause-fix",
        action="store_true",
        help="skip ensuring pause_when_empty=false in cluster.ini",
    )
    args = parser.parse_args(argv)

    game_dir = find_game_dir(args.game_dir)
    if not game_dir.exists():
        raise SystemExit(
            f"game directory not found: {game_dir}\n"
            "Download the DST dedicated server first (see README.md)."
        )
    print(f"game dir: {game_dir}")
    mods_dir = find_mods_dir(game_dir)
    install_mod(mods_dir)

    if not args.no_pause_fix:
        cluster_ini = cfg.PERSISTENT_STORAGE_ROOT / cfg.CONF_DIR / cfg.CLUSTER / "cluster.ini"
        if not cluster_ini.exists():
            print(f"warning: cluster.ini not found at {cluster_ini}; skipped pause fix")
        else:
            gp._ensure_ini_setting(cluster_ini, "GAMEPLAY", "pause_when_empty", "false")
            print("pause_when_empty = false ensured in Cluster/cluster.ini")

    print("\ndone. Next:")
    print("    tools/game_process.py start --wait-ready --lan --unpaused")
    print("    tools/run_script.py --ping")
    return 0


if __name__ == "__main__":
    sys.exit(main())
