"""Synthetic maintenance regressions; no DST process or real save is used."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SKILL_ROOT = Path(__file__).resolve().parents[2]
GENERAL = SKILL_ROOT / "references/tools/general"
sys.path.insert(0, str(GENERAL))
import check_skill as checker
import dst_zip_cache as cache


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dst-skill-maintenance-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.refs = self.root / "references"
        self.refs.mkdir()
        self.write("SKILL.md", "---\nname: dst-mod-skill-main\ndescription: fixture\n---\n")
        scope = patch.multiple(checker, REPO_ROOT=self.root, REFERENCES_ROOT=self.refs,
                               COMPONENT_REFERENCES_ROOT=self.refs / "components",
                               DOC_FILES=[self.root / "SKILL.md"])
        scope.start()
        self.addCleanup(scope.stop)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def entry_errors(self):
        checker.load_inventory()
        errors = []
        checker.check_skill_frontmatter(errors)
        return errors

    def test_only_root_entry_is_accepted(self):
        self.assertEqual(self.entry_errors(), [])

    def test_second_differently_named_entry_is_rejected(self):
        self.write("references/topic/SKILL.md", "---\nname: another-topic\ndescription: fixture\n---\n")
        self.assertTrue(any("unexpected callable skill entry" in e for e in self.entry_errors()))

    def test_missing_root_is_rejected(self):
        (self.root / "SKILL.md").unlink()
        self.assertIn("missing root SKILL.md", self.entry_errors())

    def test_incorrect_root_name_is_rejected(self):
        self.write("SKILL.md", "---\nname: another-topic\ndescription: fixture\n---\n")
        self.assertTrue(any("unexpected root skill name" in e for e in self.entry_errors()))

    def test_import_does_not_scan_directories(self):
        spec = importlib.util.spec_from_file_location("maintenance_import_fixture", GENERAL / "check_skill.py")
        module = importlib.util.module_from_spec(spec)
        with patch("os.walk", side_effect=AssertionError("import must not traverse")):
            spec.loader.exec_module(module)
        self.assertEqual(module.SCRIPT_FILES, [])

    def test_restricted_and_generated_directories_are_never_entered(self):
        denied = ["references/mod-notes", "references/knowledge/dst-engineering-kb",
                  ".git", ".codex", "references/tools/.tmp", "references/tools/__pycache__"]
        for directory in denied:
            self.write(directory + "/tools/bad.py", "this is invalid Python")
            self.write(directory + "/SKILL.md", "invalid entry")
        self.write("references/tools/allowed.py", "pass\n")
        original = os.scandir

        def guarded(path):
            path = Path(path)
            self.assertNotIn(path, [self.root / d for d in denied], "entered excluded directory")
            return original(path)

        with patch("os.scandir", side_effect=guarded):
            checker.load_inventory()
            self.assertEqual(self.entry_errors(), [])
            errors = []
            checker.check_py_compile(errors)
        self.assertEqual(errors, [])
        self.assertEqual([p.name for p in checker.SCRIPT_FILES], ["allowed.py"])

    def test_link_directories_are_pruned(self):
        self.write("linked/SKILL.md", "invalid")
        original = os.scandir

        def guarded(path):
            self.assertNotEqual(Path(path), self.root / "linked")
            return original(path)

        with patch.object(checker, "is_link", side_effect=lambda p: p.name == "linked"), \
                patch("os.scandir", side_effect=guarded):
            self.assertEqual(self.entry_errors(), [])

    def test_windows_reparse_attribute_is_treated_as_link(self):
        from types import SimpleNamespace
        with patch.object(Path, "lstat", return_value=SimpleNamespace(st_file_attributes=0x400)), \
                patch.object(Path, "is_symlink", return_value=False):
            self.assertTrue(checker.is_link(self.root / "junction"))

    def test_legacy_invocations_are_rejected_in_docs_and_metadata(self):
        self.write("references/topic/GUIDE.md", "Use $dst-networking-rpc")
        self.write("references/topic/agents/openai.yaml", 'interface:\n  default_prompt: "Use $dst-networking-rpc"\n')
        checker.load_inventory()
        errors = []
        checker.check_skill_invocations(errors)
        self.assertEqual(sum("retired skill invocation" in e for e in errors), 2)
        self.assertTrue(any("metadata must route" in e for e in errors))

    def test_root_metadata_and_topic_metadata_are_accepted(self):
        prompt = 'interface:\n  default_prompt: "Use $dst-mod-skill-main"\n'
        self.write("agents/openai.yaml", prompt)
        self.write("references/topic/GUIDE.md", "Use $dst-mod-skill-main")
        self.write("references/topic/agents/openai.yaml", prompt)
        checker.load_inventory()
        errors = []
        checker.check_skill_invocations(errors)
        self.assertEqual(errors, [])

    def test_metadata_without_guide_is_rejected(self):
        self.write("references/topic/agents/openai.yaml", 'interface:\n  default_prompt: "Use $dst-mod-skill-main"\n')
        checker.load_inventory()
        errors = []
        checker.check_skill_invocations(errors)
        self.assertTrue(any("no topic GUIDE.md" in e for e in errors))

    def test_broken_link_and_invalid_python_are_reported(self):
        self.write("references/topic/GUIDE.md", "[missing](missing.md)")
        self.write("references/tools/bad.py", "def broken(:")
        checker.load_inventory()
        errors = []
        checker.check_markdown_references(errors)
        checker.check_py_compile(errors)
        self.assertTrue(any("broken markdown link" in e for e in errors))
        self.assertTrue(any("Python syntax check failed" in e for e in errors))
        self.assertFalse(list(self.root.rglob("*.pyc")))

    def test_component_routes_accept_existing_docs_and_reject_invalid_targets(self):
        guide = "references/gameplay/combat/GUIDE.md"
        detail = "references/components/combat/deflectable.md"
        self.write(guide, "# Combat\n")
        self.write(detail, "# Deflectable\n")
        self.write("references/mod-notes/restricted.md", "# Restricted\n")
        checker.load_inventory()
        cases = [
            ({detail: ["gameplay/combat"]}, None),
            ({detail: ["gameplay/missing"]}, "missing primary topic"),
            ({"references/components/missing.md": ["gameplay/combat"]}, "invalid supporting document route"),
            ({"references/mod-notes/restricted.md": ["gameplay/combat"]}, "invalid supporting document route"),
        ]
        for routes, expected in cases:
            with self.subTest(routes=routes):
                self.write("references/knowledge/document-routes.json",
                           json.dumps({"schema_version": 1, "supporting_documents": routes}))
                errors = []
                checker.check_document_routes(errors)
                if expected is None:
                    self.assertEqual(errors, [])
                else:
                    self.assertTrue(any(expected in error for error in errors), errors)

    def test_default_cache_is_outside_skill(self):
        skill = self.root / ".trae/skills/dst-mod-skill-main"
        self.assertEqual(cache.default_cache_root(skill), self.root / ".codex/cache/dst-zip")
        self.assertFalse(cache.default_cache_root(self.root / "standalone").is_relative_to(self.root / "standalone"))

    def test_cache_override_and_roundtrip(self):
        archive = self.root / "scripts.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("scripts/main.lua", "return true")
        override = self.root / "cache-override"
        with patch.dict(os.environ, {"DST_ZIP_CACHE_DIR": str(override)}):
            subject = cache.ZipContextCache(archive)
            self.assertEqual(subject.root, override)
            subject.store_entry_names(["scripts/main.lua"])
            subject.store_text_lines("scripts/main.lua", ["return true"])
            self.assertEqual(subject.load_entry_names(), ["scripts/main.lua"])
            self.assertEqual(subject.load_text_lines("scripts/main.lua"), ["return true"])


class PowerShellEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shell = shutil.which("pwsh") or shutil.which("powershell")
        if cls.shell is None:
            raise unittest.SkipTest("PowerShell is unavailable")

    def invoke(self, *args):
        return subprocess.run([self.shell, "-NoProfile", "-File",
                               str(SKILL_ROOT / "references/tools/engineering/run.ps1"), *args],
                              capture_output=True, text=True, encoding="utf-8", timeout=30)

    def test_old_and_new_commands_keep_same_target_and_exit_code(self):
        for old, new in [("check_api", "check_api_ast"), ("dst_zip_tool", "zip_read")]:
            with self.subTest(command=new):
                legacy = self.invoke(old, "--help")
                current = self.invoke(new, "--help")
                self.assertEqual(legacy.returncode, 0, legacy.stderr)
                self.assertEqual(current.returncode, legacy.returncode, current.stderr)
                self.assertEqual(current.stdout, legacy.stdout)
                self.assertEqual(current.stderr, legacy.stderr)

    def test_fast_and_ast_commands_have_distinct_help(self):
        fast = self.invoke("check_api_fast", "--help")
        ast = self.invoke("check_api_ast", "--help")
        self.assertEqual(fast.returncode, 0, fast.stderr)
        self.assertEqual(ast.returncode, 0, ast.stderr)
        self.assertNotEqual(fast.stdout, ast.stdout)

    def test_exit_code_and_json_stdout_are_preserved(self):
        with tempfile.TemporaryDirectory(prefix="dst-skill-entry-") as directory:
            archive = Path(directory) / "scripts.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("scripts/main.lua", "return true")
            info = self.invoke("zip_read", "--zip", str(archive), "info")
            self.assertEqual(info.returncode, 0, info.stderr)
            self.assertEqual(json.loads(info.stdout)["lua_files"], 1)
            missing = self.invoke("zip_read", "--zip", str(archive), "grep", "nonexistent")
            self.assertEqual(missing.returncode, 1, missing.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
