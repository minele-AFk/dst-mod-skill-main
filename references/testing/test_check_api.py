"""Regression tests: python -B references/testing/test_check_api.py"""

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "general"))
import check_api as api


class ApiCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dst-api-check-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "源码 parent" / "scripts"
        self.root.mkdir(parents=True)
        (self.root / "components").mkdir()
        self.write_source("entityscript.lua", "function EntityScript:IsValid() end")
        self.write_source("entityreplica.lua", "function EntityScript:ReplicateComponent(name) end")
        self.write_source("components/hunger.lua", """
local Hunger = Class(function(self, inst)
    self.current = 100
    self.callback = some_callback
    self.CustomFn = function() end
end)
function Hunger:DoDelta(amount) end
return Hunger
""")
        self.write_source("components/hunger_replica.lua", "function Hunger:GetCurrent() end")
        self.lua = Path(self.tmp.name) / "待检查.lua"

    def write_source(self, rel, content):
        (self.root / rel).write_text(content, encoding="utf-8")

    def run_cli(self, code, *options):
        self.lua.write_text(code, encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = api.main([str(self.lua), *options])
        return result, output.getvalue()

    def directory_cli(self, code):
        return self.run_cli(code, "--scripts-dir", str(self.root))

    def make_zip(self, prefix="scripts/"):
        path = Path(self.tmp.name) / "scripts.zip"
        with zipfile.ZipFile(path, "w") as archive:
            for source in self.root.rglob("*.lua"):
                archive.write(source, prefix + source.relative_to(self.root).as_posix())
        return path

    def test_scripts_directory_and_parent_are_equivalent(self):
        for root in (self.root, self.root.parent):
            with self.subTest(root=root):
                self.assertEqual(self.run_cli("inst.components.hunger:DoDelta(1)",
                                             "--scripts-dir", str(root))[0], 0)

    def test_zip_with_and_without_scripts_prefix(self):
        for prefix in ("scripts/", ""):
            with self.subTest(prefix=prefix):
                self.assertEqual(self.run_cli("inst.components.hunger:DoDelta(1)",
                                             "--zip", str(self.make_zip(prefix)))[0], 0)

    def test_master_component_does_not_inherit_replica_methods(self):
        status, output = self.directory_cli("inst.components.hunger:GetCurrent()")
        self.assertEqual(status, 1)
        self.assertIn("components.hunger:GetCurrent", output)

    def test_replica_does_not_inherit_master_methods(self):
        self.assertEqual(self.directory_cli("inst.replica.hunger:DoDelta(1)")[0], 1)

    def test_declared_replica_method_matches(self):
        self.assertEqual(self.directory_cli("inst.replica.hunger:GetCurrent()")[0], 0)

    def test_numeric_field_is_not_verified_as_method(self):
        status, output = self.directory_cli("inst.components.hunger:current()")
        self.assertEqual(status, 3)
        self.assertIn("callability", output)

    def test_callback_field_requires_review(self):
        self.assertEqual(self.directory_cli("inst.components.hunger:callback()")[0], 3)

    def test_explicit_function_field_matches(self):
        self.assertEqual(self.directory_cli("inst.components.hunger:CustomFn()")[0], 0)

    def test_alias_with_other_valid_call_cannot_silently_pass(self):
        status, output = self.directory_cli("""
inst.components.hunger:DoDelta(1)
local h = inst.components.hunger
h:DefinitelyMissing()
""")
        self.assertEqual(status, 3)
        self.assertIn("alias", output)

    def test_computed_access_requires_review(self):
        self.assertEqual(self.directory_cli('inst.components["hunger"]:DoDelta(1)')[0], 3)

    def test_custom_component_requires_review(self):
        self.assertEqual(self.directory_cli("inst.components.mycustom:Run()")[0], 3)

    def test_dynamic_entity_method_requires_review(self):
        self.assertEqual(self.directory_cli("inst:EngineOrPrefabMethod()")[0], 3)

    def test_entityreplica_extensions_are_indexed(self):
        self.assertEqual(self.directory_cli('inst:ReplicateComponent("hunger")')[0], 0)

    def test_comments_and_strings_are_not_checked(self):
        status, output = self.directory_cli('''
-- inst.components.hunger:Missing()
--[=[ inst.components.hunger:Missing() ]=]
local s = "inst.components.hunger:Missing() -- escaped \\\" text"
local t = [==[inst.components.hunger:Missing()]==]
inst.components.hunger:DoDelta(1)
''')
        self.assertEqual(status, 0, output)
        self.assertIn("1 examined direct call", output)

    def test_error_has_original_file_and_line(self):
        status, output = self.directory_cli('-- comment\nlocal s = "x"\ninst.components.hunger:Missing()')
        self.assertEqual(status, 1)
        self.assertIn(str(self.lua) + ":3", output)

    def test_zero_calls_is_review(self):
        self.assertEqual(self.directory_cli("local x = 1")[0], 3)

    def test_missing_input_is_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(api.main([str(Path(self.tmp.name) / "missing.lua")]), 2)

    def test_empty_input_directory_is_error(self):
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(api.main([str(empty)]), 2)

    def test_bad_source_directory_is_error(self):
        self.assertEqual(self.run_cli("inst:IsValid()", "--scripts-dir", self.tmp.name)[0], 2)

    def test_bad_zip_is_error(self):
        path = Path(self.tmp.name) / "bad.zip"
        path.write_bytes(b"not a zip")
        self.assertEqual(self.run_cli("inst:IsValid()", "--zip", str(path))[0], 2)

    def test_empty_component_index_is_error(self):
        for source in (self.root / "components").glob("*.lua"):
            source.unlink()
        self.assertEqual(self.directory_cli("inst:IsValid()")[0], 2)

    def test_source_environment_override(self):
        with patch.dict("os.environ", {"DST_SCRIPTS_DIR": str(self.root)}):
            self.assertEqual(self.run_cli("inst:IsValid()")[0], 0)

    def test_explicit_zip_overrides_environment_directory(self):
        with patch.dict("os.environ", {"DST_SCRIPTS_DIR": "missing-directory"}):
            self.assertEqual(self.run_cli("inst:IsValid()", "--zip", str(self.make_zip()))[0], 0)

    def test_unpacked_dst_override(self):
        self.assertEqual(self.run_cli("inst:IsValid()", "--dst", str(self.root.parent))[0], 0)

    def test_duplicate_inputs_are_deduplicated(self):
        self.lua.write_text("inst:IsValid()", encoding="utf-8")
        self.assertEqual(len(api.lua_files_from_args([str(self.lua), str(self.lua)])), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
