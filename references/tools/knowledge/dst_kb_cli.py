from pathlib import Path
import sys


def main():
    arguments = sys.argv[1:]
    if arguments in (["--help"], ["-h"]):
        print("Read-only DST skill knowledge. Run from the skill directory or use run.ps1 knowledge.\n"
              "  lookup QUERY [--mode MODE] [--limit 1..10]  Local docs + structured evidence\n"
              "  docs QUERY [--limit 1..10]                 Local references only\n"
              "  read PATH [--start N] [--count 1..200]      Read a permitted reference section\n"
              "  catalog                                   Report local corpus scope\n"
              "  topics [--query TEXT] [--limit 0..50]     Ranked topic routes and supporting pages\n"
              "  status | validate | reindex | call | serve Existing structured KB commands\n"
              "Use COMMAND --help for local commands; --config PATH may precede COMMAND.")
        return 0
    command = arguments[0] if arguments else None
    if command == '--config':
        command = arguments[2] if len(arguments) > 2 else None
    elif command and command.startswith('--config='):
        command = arguments[1] if len(arguments) > 1 else None
    if command in {'lookup', 'docs', 'read', 'catalog', 'topics'}:
        from skill_knowledge import main as local_main
        return local_main(arguments)
    from dst_kb.cli import main as evidence_main
    if not any(arg == '--config' or arg.startswith('--config=') for arg in arguments):
        sys.argv[1:1] = ['--config', str(Path(__file__).with_name('config.json'))]
    evidence_main()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
