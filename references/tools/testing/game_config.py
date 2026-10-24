"""Shared configuration for the DST test-server tools.

All paths default to the repository layout:

    <root>/dontstarvetogether_dedicated_server/.../Contents/mods/dst_test_mod/
    <root>/Cluster/Master/                    <- the game's shard directory

The Cluster/Master layout in this repo is exactly the game's
<persistent_storage_root>/<conf_dir>/<cluster>/<shard> structure, so by
default persistent_storage_root points at the repo's parent directory and
conf_dir is the repo directory name.

Every value can be overridden through environment variables:
    DST_SERVER_ROOT             repo root
    DST_PERSISTENT_STORAGE_ROOT -persistent_storage_root
    DST_CONF_DIR                -conf_dir
    DST_CLUSTER                 -cluster
    DST_SHARD                   -shard
    DST_LAN                     "1"/"true"/"yes" to default to LAN-only mode
"""

import os
from pathlib import Path

ROOT = Path(os.environ.get("DST_SERVER_ROOT", Path(__file__).resolve().parent.parent))

SERVER_DIR = ROOT / "dontstarvetogether_dedicated_server"
APP_DIR = SERVER_DIR / "dontstarve_dedicated_server_nullrenderer.app"
CONTENTS_DIR = APP_DIR / "Contents"
BINARY = CONTENTS_DIR / "MacOS" / "dontstarve_dedicated_server_nullrenderer"
MODS_DIR = CONTENTS_DIR / "mods"

MOD_NAME = "dst_test_mod"
MOD_DIR = MODS_DIR / MOD_NAME
REQUEST_FILE = MOD_DIR / "scripts" / "test_request.lua"

PERSISTENT_STORAGE_ROOT = Path(
    os.environ.get("DST_PERSISTENT_STORAGE_ROOT", str(ROOT.parent))
)
CONF_DIR = os.environ.get("DST_CONF_DIR", ROOT.name)
CLUSTER = os.environ.get("DST_CLUSTER", "Cluster")
SHARD = os.environ.get("DST_SHARD", "Master")

SHARD_DIR = PERSISTENT_STORAGE_ROOT / CONF_DIR / CLUSTER / SHARD
SAVE_DIR = SHARD_DIR / "save"

# The game only allows runtime file writes under data/unsafedata/ (flat
# directory, .txt/.tex/.xml/.png/.json extensions).  Responses are written
# there by the test mod and cleaned up by tools/run_script.py.
UNSAFEDATA_DIR = CONTENTS_DIR / "data" / "unsafedata"
RESPONSE_DIR = UNSAFEDATA_DIR
RESPONSE_PREFIX = "dst_test_response_"
RESPONSE_GLOB = RESPONSE_PREFIX + "*.txt"

SERVER_LOG = SHARD_DIR / "server_log.txt"
SERVER_CHAT_LOG = SHARD_DIR / "server_chat_log.txt"
CONSOLE_LOG = ROOT / "tools" / "server_console.log"
PID_FILE = ROOT / "tools" / "server.pid"

LAN_DEFAULT = os.environ.get("DST_LAN", "0") in ("1", "true", "yes")
