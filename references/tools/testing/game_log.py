#!/usr/bin/env python3
"""Read DST server log files.

Usage:
    game_log.py paths
    game_log.py tail [N] [--chat] [--console]
    game_log.py grep PATTERN [N] [--chat] [--console] [--ignore-case]
    game_log.py follow [--until PATTERN] [--timeout N] [--chat] [--console]

By default the active shard log (server_log.txt) is used.  --chat selects
the chat log and --console the captured stdout/stderr of the server process.
If the active log has been rotated away, the newest backup log is used.
"""

import argparse
import glob
import os
import re
import sys
import time
from pathlib import Path

import game_config as cfg


READY_PATTERNS = ["Server registered", "Sim paused", "Sim unpaused"]


def _backup_logs():
    backup_dir = cfg.SHARD_DIR / "backup"
    if not backup_dir.is_dir():
        return []
    return sorted(backup_dir.glob("*server_log*"), key=lambda p: p.stat().st_mtime, reverse=True)


def _resolve_log_path(kind):
    if kind == "chat":
        return cfg.SERVER_CHAT_LOG
    if kind == "console":
        return cfg.CONSOLE_LOG
    if cfg.SERVER_LOG.exists():
        return cfg.SERVER_LOG
    backups = _backup_logs()
    return backups[0] if backups else cfg.SERVER_LOG


def _read_lines(path, start=0):
    """Return lines of a log file, tolerating odd encodings and \r."""
    if not path.exists():
        return []
    with open(path, "rb") as f:
        if start:
            f.seek(start)
        raw = f.read()
    text = raw.decode("utf-8", errors="replace")
    return text.splitlines()


def _file_offset(path):
    return path.stat().st_size if path.exists() else 0


def cmd_paths():
    print(f"root: {cfg.ROOT}")
    print(f"binary: {cfg.BINARY}")
    print(f"shard dir: {cfg.SHARD_DIR}")
    print(f"server log: {cfg.SERVER_LOG}")
    print(f"chat log: {cfg.SERVER_CHAT_LOG}")
    print(f"console log: {cfg.CONSOLE_LOG}")
    print(f"request file: {cfg.REQUEST_FILE}")
    print(f"response dir: {cfg.RESPONSE_DIR}")
    print(f"response glob: {cfg.RESPONSE_GLOB}")


def cmd_tail(args):
    path = _resolve_log_path(args.source)
    lines = _read_lines(path)
    n = args.lines or 10
    for line in lines[-n:]:
        print(line)


def cmd_grep(args):
    path = _resolve_log_path(args.source)
    lines = _read_lines(path)
    flags = re.IGNORECASE if args.ignore_case else 0
    pattern = re.compile(args.pattern, flags)
    matches = [line for line in lines if pattern.search(line)]
    n = args.lines or 50
    for line in matches[-n:]:
        print(line)


def cmd_follow(args):
    path = _resolve_log_path(args.source)
    offset = _file_offset(path)
    deadline = None
    if args.timeout and args.timeout > 0:
        deadline = time.time() + args.timeout

    pattern = None
    if args.until:
        pattern = re.compile(args.until)

    while True:
        current = _file_offset(path)
        if current < offset:
            offset = 0  # log was rotated/truncated
        for line in _read_lines(path, start=offset):
            print(line)
            if pattern and pattern.search(line):
                return 0
        offset = current

        if deadline and time.time() > deadline:
            return 1
        time.sleep(0.5)


def wait_for_pattern(patterns, timeout=120, sources=("server", "console")):
    """Block until one of the patterns appears in a log source. Returns bool."""
    patterns = [re.compile(p) for p in patterns]
    offsets = {}
    deadline = time.time() + timeout

    while time.time() < deadline:
        for kind in sources:
            path = _resolve_log_path(kind)
            offset = offsets.get(kind, _file_offset(path))
            current = _file_offset(path)
            if current < offset:
                offset = 0
            for line in _read_lines(path, start=offset):
                if any(p.search(line) for p in patterns):
                    return True
            offsets[kind] = current
        time.sleep(0.5)
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    sub.add_parser("paths", help="print resolved file paths")

    p_tail = sub.add_parser("tail", help="print the last N log lines")
    p_tail.add_argument("lines", nargs="?", type=int, default=10, help="number of lines (default 10)")
    p_tail.add_argument("--chat", dest="source", action="store_const", const="chat", default="server")
    p_tail.add_argument("--console", dest="source", action="store_const", const="console")

    p_grep = sub.add_parser("grep", help="print matching log lines")
    p_grep.add_argument("pattern")
    p_grep.add_argument("lines", nargs="?", type=int, default=50, help="max matches (default 50)")
    p_grep.add_argument("--ignore-case", action="store_true")
    p_grep.add_argument("--chat", dest="source", action="store_const", const="chat", default="server")
    p_grep.add_argument("--console", dest="source", action="store_const", const="console")

    p_follow = sub.add_parser("follow", help="stream new log lines")
    p_follow.add_argument("--until", help="stop when a line matches this regex")
    p_follow.add_argument("--timeout", type=int, default=0, help="max seconds to wait (0 = forever)")
    p_follow.add_argument("--chat", dest="source", action="store_const", const="chat", default="server")
    p_follow.add_argument("--console", dest="source", action="store_const", const="console")

    args = parser.parse_args(argv)

    if args.action == "paths":
        cmd_paths()
    elif args.action == "tail":
        cmd_tail(args)
    elif args.action == "grep":
        cmd_grep(args)
    elif args.action == "follow":
        return cmd_follow(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
