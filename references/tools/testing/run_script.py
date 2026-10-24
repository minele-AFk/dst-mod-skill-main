#!/usr/bin/env python3
"""Inject Lua code into the running DST server and return its result.

Usage:
    run_script.py --code "return TheWorld and TheWorld.state.cycles or 0"
    run_script.py --file /tmp/test.lua
    run_script.py --timeout 30 --json <<'EOF'
    local player = GLOBAL.ThePlayer
    print("hello", player and player.name or "nobody")
    return 1 + 1
    EOF

The code is written to the test mod's request file
(.../mods/dst_test_mod/scripts/test_request.lua) with a modification time
that is guaranteed to differ from the previous one.  The mod polls that file
every 1/30 s, runs the code with xpcall, and writes a response to a fresh
data/unsafedata/dst_test_response_<mtime>.txt via io.open (the only runtime
file write the game permits).  The game has no file-deletion API, so this
script removes stale response files.  It then waits for the new response and
prints the return values and any print() output.

Exit codes:
    0  script ran and returned (status ok)
    1  script ran but raised an error (status error)
    2  timed out waiting for a response
    3  server is not running
"""

import argparse
import ast
import fcntl
import json
import os
import re
import sys
import time

import game_config as cfg
import game_process as gp


RESPONSE_BEGIN = "--dst-test-response--"
RESPONSE_END = "--dst-test-response-end--"


def _strip_klei_header(text):
    m = re.match(r"^KLEI\s+\d+\s+", text)
    return text[m.end():] if m else text


def _decode_value(line):
    value = line.strip()
    if value == "nil":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith("number:"):
        text = value[len("number:"):]
        try:
            return float(text)
        except ValueError:
            return text
    if value.startswith("string:"):
        raw = value[len("string:"):]
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return raw
    if value.startswith("table:"):
        return value[len("table:"):]
    if value.startswith("function:"):
        return "<function>"
    return value


def _parse_mtime(text):
    text = text.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        pass
    # The game can report file times as 16-digit hex (e.g. 000000006a71e141).
    if re.fullmatch(r"[0-9a-fA-F]+", text):
        return float(int(text, 16))
    return None


def parse_response(text):
    """Parse a response file into a dict; return None if incomplete."""
    text = _strip_klei_header(text)
    if RESPONSE_BEGIN not in text or RESPONSE_END not in text:
        return None

    status = None
    mtime = None
    values = []
    prints = []
    section = None

    lines = text.splitlines()
    started = False
    for line in lines:
        stripped = line.strip()
        if not started:
            if stripped == RESPONSE_BEGIN:
                started = True
            continue
        if stripped == RESPONSE_END:
            break
        if stripped.startswith("status:"):
            status = stripped[len("status:"):].strip()
            continue
        if stripped.startswith("mtime:"):
            mtime = _parse_mtime(stripped[len("mtime:"):])
            continue
        if stripped == "values:":
            section = "values"
            continue
        if stripped == "prints:":
            section = "prints"
            continue
        if section == "values" and stripped:
            values.append(_decode_value(stripped))
        elif section == "prints":
            prints.append(line)

    if status is None:
        return None
    return {
        "status": status,
        "mtime": mtime,
        "values": values,
        "prints": prints,
        "error": "\n".join(prints) if status == "error" else None,
    }


def _read_code(args):
    if args.ping:
        return 'return "pong"'
    if args.code is not None:
        return args.code
    if args.file:
        return open(args.file, encoding="utf-8").read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("no code given; use --code, --file, --ping, or pipe stdin")


def _response_files():
    return sorted(
        cfg.RESPONSE_DIR.glob(cfg.RESPONSE_GLOB),
        key=lambda p: p.stat().st_mtime,
    )


def _bump_mtime(path):
    current = path.stat().st_mtime if path.exists() else 0.0
    new_mtime = max(time.time(), current + 1.0)
    os.utime(path, (new_mtime, new_mtime))
    return new_mtime


def run(code, timeout=30, json_output=False):
    pid, _ = gp.is_running()
    if not pid:
        print(
            "server is not running; start it with tools/game_process.py start",
            file=sys.stderr,
        )
        raise SystemExit(3)

    lock_path = cfg.ROOT / "tools" / ".run_script.lock"
    lock_file = open(lock_path, "a+")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)

        cfg.REQUEST_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = "-- dst-test request (written by tools/run_script.py)\n" + code
        cfg.REQUEST_FILE.write_text(payload, encoding="utf-8")
        _bump_mtime(cfg.REQUEST_FILE)

        # Drop any stale responses so a fresh one is unambiguous.
        for old in _response_files():
            try:
                old.unlink()
            except OSError:
                pass

        deadline = time.time() + timeout
        last_touch = time.time()

        while time.time() < deadline:
            for response in _response_files():
                try:
                    text = response.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    text = ""
                parsed = parse_response(text)
                if parsed is not None:
                    _report(parsed, json_output)
                    return 0 if parsed["status"] == "ok" else 1

            # If the bridge missed the first write (e.g. it had just recorded
            # a baseline), re-touch the file so the mtime changes again.
            if time.time() - last_touch > 3.0:
                _bump_mtime(cfg.REQUEST_FILE)
                last_touch = time.time()

            time.sleep(0.2)

        _report(
            {
                "status": "timeout",
                "values": [],
                "prints": [],
                "error": f"no response within {timeout}s",
            },
            json_output,
        )
        return 2
    finally:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()


def _report(parsed, json_output):
    if json_output:
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        return
    print(f"status: {parsed['status']}")
    if parsed.get("mtime") is not None:
        print(f"mtime: {parsed['mtime']}")
    if parsed["values"]:
        print("values:")
        for v in parsed["values"]:
            if isinstance(v, str):
                print("  " + json.dumps(v, ensure_ascii=False))
            else:
                print("  " + json.dumps(v, ensure_ascii=False))
    if parsed["prints"]:
        print("prints:")
        for line in parsed["prints"]:
            print("  " + line)
    if parsed.get("error"):
        print(f"error: {parsed['error']}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", help="Lua code to run")
    parser.add_argument("--file", help="read Lua code from a file")
    parser.add_argument("--ping", action="store_true", help="run a trivial `return \"pong\"` probe")
    parser.add_argument("--timeout", type=int, default=30, help="max seconds to wait for a response (default 30)")
    parser.add_argument("--json", action="store_true", help="machine readable output")
    args = parser.parse_args(argv)

    code = _read_code(args)
    return run(code, timeout=args.timeout, json_output=args.json)


if __name__ == "__main__":
    sys.exit(main())
