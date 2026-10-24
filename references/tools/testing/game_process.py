#!/usr/bin/env python3
"""Start, stop and report the status of the DST dedicated server.

Usage:
    game_process.py start [--wait-ready] [--timeout N] [--lan] [--unpaused]
    game_process.py stop [--timeout N]
    game_process.py status [--json]
    game_process.py restart [--wait-ready] [--timeout N] [--lan] [--unpaused]

The server is launched with the persistent storage layout configured in
game_config.py (defaults to this repo's Cluster/ folder).  Its console
output is appended to tools/server_console.log and its pid is stored in
tools/server.pid.
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import game_config as cfg
from game_log import wait_for_pattern


# ---------------------------------------------------------------------------
# process helpers
# ---------------------------------------------------------------------------

def _run(cmd):
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _command_of(pid):
    return _run(["ps", "-p", str(pid), "-o", "command="])


def _state_of(pid):
    return _run(["ps", "-p", str(pid), "-o", "stat="]).strip()


def _process_alive(pid):
    if not pid:
        return False
    state = _state_of(pid)
    if state:
        if state.startswith("Z"):
            return False  # zombie: not really running anymore
        return True
    # ps is unavailable (restricted environment); fall back to kill(0).
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # The process exists but belongs to someone else (or the sandbox
        # forbids signaling); treat it as running.
        return True
    except OSError:
        return False


def _recently_written_log():
    """True when the shard log was touched in the last few minutes."""
    if not cfg.SERVER_LOG.exists():
        return False
    return time.time() - cfg.SERVER_LOG.stat().st_mtime < 300


def _find_pids_by_name():
    """Find server processes by binary name using pgrep -f."""
    out = _run(["pgrep", "-f", "dontstarve_dedicated_server_nullrenderer"])
    pids = []
    for token in out.split():
        if token.isdigit():
            pids.append(int(token))
    return pids


def _matches_server(pid):
    cmd = _command_of(pid)
    return "dontstarve_dedicated_server" in cmd


def is_running():
    """Return (pid, command_line) for the running server, or (None, None)."""
    if cfg.PID_FILE.exists():
        try:
            pid = int(cfg.PID_FILE.read_text(encoding="utf-8").strip())
        except ValueError:
            pid = None
        if pid and _process_alive(pid) and (
            _matches_server(pid) or _recently_written_log()
        ):
            return pid, _command_of(pid)

    # Fall back to scanning the process table.
    for pid in _find_pids_by_name():
        if _process_alive(pid) and (
            _matches_server(pid) or _recently_written_log()
        ):
            return pid, _command_of(pid)
    return None, None


# ---------------------------------------------------------------------------
# cluster.ini helpers
# ---------------------------------------------------------------------------

def _get_ini_setting(path, section, key):
    if not path.exists():
        return None
    section = section.strip().lower()
    key = key.strip().lower()
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1].strip().lower()
            continue
        if current != section:
            continue
        if "=" in stripped:
            k, _, v = stripped.partition("=")
            if k.strip().lower() == key:
                return v.strip()
    return None


def _ensure_ini_setting(path, section, key, value):
    """Idempotently set key = value inside [section], preserving the file."""
    if not path.exists():
        raise FileNotFoundError(f"missing cluster.ini: {path}")
    section = section.strip().lower()
    key = key.strip().lower()
    lines = path.read_text(encoding="utf-8").splitlines()

    current = None
    section_index = None
    insert_index = None
    replaced = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            name = stripped[1:-1].strip().lower()
            if name == section:
                current = name
                section_index = i
                insert_index = i + 1
            elif current == section:
                break
            continue
        if current == section and "=" in stripped:
            k, _, v = stripped.partition("=")
            if k.strip().lower() == key:
                lines[i] = f"{key} = {value}"
                replaced = True
                insert_index = None
                break

    if section_index is None:
        lines.append("")
        lines.append(f"[{section}]")
        lines.append(f"{key} = {value}")
    elif not replaced and insert_index is not None:
        lines.insert(insert_index, f"{key} = {value}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# actions
# ---------------------------------------------------------------------------

def start(wait_ready=False, timeout=120, lan=False, unpaused=False):
    pid, _ = is_running()
    if pid:
        print(f"server already running (pid {pid})")
        return pid

    if not cfg.BINARY.exists():
        raise SystemExit(f"server binary not found: {cfg.BINARY}")

    cluster_ini = cfg.PERSISTENT_STORAGE_ROOT / cfg.CONF_DIR / cfg.CLUSTER / "cluster.ini"
    if lan:
        _ensure_ini_setting(cluster_ini, "NETWORK", "lan_only_cluster", "true")
        print("lan_only_cluster = true set in cluster.ini")
    if unpaused:
        _ensure_ini_setting(cluster_ini, "GAMEPLAY", "pause_when_empty", "false")
        print("pause_when_empty = false set in cluster.ini")
    elif _get_ini_setting(cluster_ini, "GAMEPLAY", "pause_when_empty") == "true":
        print(
            "warning: pause_when_empty=true pauses the sim while empty; "
            "the test bridge will not poll. Re-run with --unpaused."
        )

    cfg.SHARD_DIR.mkdir(parents=True, exist_ok=True)
    cfg.SAVE_DIR.mkdir(parents=True, exist_ok=True)

    console = open(cfg.CONSOLE_LOG, "ab")
    cmd = [
        str(cfg.BINARY),
        "-persistent_storage_root", str(cfg.PERSISTENT_STORAGE_ROOT),
        "-conf_dir", cfg.CONF_DIR,
        "-cluster", cfg.CLUSTER,
        "-shard", cfg.SHARD,
        "-skip_update_server_mods",
    ]
    env = dict(os.environ, SteamAppId="322330", SteamGameId="322330")
    proc = subprocess.Popen(
        cmd,
        cwd=str(cfg.CONTENTS_DIR),
        stdin=subprocess.DEVNULL,
        stdout=console,
        stderr=subprocess.STDOUT,
        env=env,
        start_new_session=True,
    )
    console.close()
    cfg.PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    print(f"started pid {proc.pid}: {' '.join(cmd)}")

    if wait_ready:
        ok = wait_for_pattern(
            ["Server registered", "Sim paused", "Sim unpaused"],
            timeout=timeout,
        )
        if not ok:
            print("timed out waiting for the server to become ready")
            return proc.pid
        print("server is ready")
    return proc.pid


def stop(timeout=30):
    pid, _ = is_running()
    if not pid:
        print("server is not running")
        return 0

    print(f"stopping pid {pid}")
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    deadline = time.time() + timeout
    while time.time() < deadline and _process_alive(pid):
        time.sleep(0.5)

    if _process_alive(pid):
        print(f"pid {pid} did not exit within {timeout}s, sending SIGKILL")
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        time.sleep(1)

    if cfg.PID_FILE.exists():
        cfg.PID_FILE.unlink()
    print("server stopped")
    return 0


def status(as_json=False):
    pid, cmd = is_running()
    info = {
        "running": pid is not None,
        "pid": pid,
        "command": cmd or "",
        "cluster": cfg.CLUSTER,
        "shard": cfg.SHARD,
        "shard_dir": str(cfg.SHARD_DIR),
        "log_file": str(cfg.SERVER_LOG),
        "log_exists": cfg.SERVER_LOG.exists(),
        "log_modified": None,
        "response_dir": str(cfg.RESPONSE_DIR),
        "response_prefix": cfg.RESPONSE_PREFIX,
    }
    if cfg.SERVER_LOG.exists():
        info["log_modified"] = cfg.SERVER_LOG.stat().st_mtime

    if as_json:
        print(json.dumps(info, indent=2))
    else:
        state = "running" if pid else "stopped"
        print(f"server: {state}")
        if pid:
            print(f"pid: {pid}")
            print(f"command: {cmd}")
        print(f"cluster: {cfg.CLUSTER}  shard: {cfg.SHARD}")
        print(f"shard dir: {cfg.SHARD_DIR}")
        print(f"log: {cfg.SERVER_LOG}")
        if info["log_modified"]:
            print(f"log last modified: {time.ctime(info['log_modified'])}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    p_start = sub.add_parser("start", help="start the server")
    p_start.add_argument("--wait-ready", action="store_true", help="wait until the server finishes booting")
    p_start.add_argument("--timeout", type=int, default=120, help="boot timeout in seconds (default 120)")
    p_start.add_argument("--lan", action="store_true", help="set lan_only_cluster=true in cluster.ini first")
    p_start.add_argument("--unpaused", action="store_true", help="set pause_when_empty=false in cluster.ini first")

    p_stop = sub.add_parser("stop", help="stop the server")
    p_stop.add_argument("--timeout", type=int, default=30, help="graceful shutdown timeout in seconds")

    p_status = sub.add_parser("status", help="show server status")
    p_status.add_argument("--json", action="store_true", help="machine readable output")

    p_restart = sub.add_parser("restart", help="stop then start the server")
    p_restart.add_argument("--wait-ready", action="store_true")
    p_restart.add_argument("--timeout", type=int, default=120)
    p_restart.add_argument("--lan", action="store_true")
    p_restart.add_argument("--unpaused", action="store_true")

    args = parser.parse_args(argv)

    if args.action == "start":
        start(wait_ready=args.wait_ready, timeout=args.timeout, lan=args.lan, unpaused=args.unpaused)
    elif args.action == "stop":
        return stop(timeout=args.timeout)
    elif args.action == "status":
        return status(as_json=args.json)
    elif args.action == "restart":
        stop(timeout=args.timeout)
        start(wait_ready=args.wait_ready, timeout=args.timeout, lan=args.lan, unpaused=args.unpaused)
    return 0


if __name__ == "__main__":
    sys.exit(main())
