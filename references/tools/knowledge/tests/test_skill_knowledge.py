"""Knowledge retrieval behavior and permission boundaries; no game process."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import skill_knowledge as knowledge


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dst-skill-knowledge-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("SKILL.md", "# Entry\nChoose a topic.\n")
        (self.root / "references").mkdir()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_title_and_specific_topic_rank_above_navigation(self):
        expected = "references/core/network/GUIDE.md"
        self.write(expected, "# 联机 RPC\n\n## 初始同步\n远端客户端初始化读取 netvar。\n")
        self.write("references/topic-index.md", "# 目录\n联机 RPC 初始同步、食物、动画。\n")
        result = knowledge.Corpus(self.root).search("RPC 初始同步")
        self.assertEqual(result["results"][0]["path"], expected)
        row = result["results"][0]
        source = (self.root / expected).read_text(encoding="utf-8").splitlines()
        self.assertIn(source[row["line"] - 1], row["snippet"])
        self.assertTrue(row["direct_match"])

    def test_full_api_identifier_outweighs_fragments_and_selects_its_line(self):
        expected = "references/components/combat.md"
        self.write(expected, "# Combat\nGet Get Get\n调用 GetAttacked_Internal 完成受击。\n")
        self.write("references/save/GUIDE.md",
                   "---\ndescription: GetPersistData GetSaveRecord\n---\n# Get save data\n")
        self.write("references/components/unrelated.md", "# GetAttacked_InternalExtra\nGet save data。\n")
        corpus = knowledge.Corpus(self.root)
        for query in ("GetAttacked_Internal", "getattacked_internal", "包装 GetAttacked_Internal"):
            with self.subTest(query=query):
                row = corpus.search(query, limit=1)["results"][0]
                self.assertEqual(row["path"], expected)
                self.assertEqual(row["line"], 3)
                self.assertIn("GetAttacked_Internal", row["snippet"])
                self.assertEqual(row["exact_symbol_matches"], ["getattacked_internal"])
                self.assertTrue(row["direct_match"])

    def test_document_review_metadata_overrides_collection_defaults(self):
        explicit = "references/explicit.md"
        fallback = "references/fallback.md"
        for path in (explicit, fallback):
            self.write(path, "# Review fixture\n复核元数据。\n")
        documents = {path: {"sha256": hashlib.sha256((self.root / path).read_bytes()).hexdigest(),
                            "depth": "content_curated"} for path in (explicit, fallback)}
        documents[explicit].update(reviewed_on="2026-10-21", source_snapshot_sha256="older-source")
        self.write("references/knowledge/review-status.json", json.dumps({
            "schema_version": 1, "reviewed_on": "2026-10-24",
            "source_snapshot": {"sha256": "collection-source"}, "documents": documents}))
        corpus = knowledge.Corpus(self.root)
        rows = {row["path"]: row["maintenance"] for row in corpus.search("Review fixture")["results"]}
        for path, date, snapshot in ((explicit, "2026-10-21", "older-source"),
                                     (fallback, "2026-10-24", "collection-source")):
            with self.subTest(path=path):
                for metadata in (rows[path], knowledge.read_reference(self.root, path)["maintenance"]):
                    self.assertEqual(metadata["status"], "record_current")
                    self.assertEqual(metadata["reviewed_on"], date)
                    self.assertEqual(metadata["source_snapshot_sha256"], snapshot)
                    self.assertEqual(metadata["runtime_validation"], "not_established_by_this_review")
        self.write(explicit, "# Changed after review\n")
        self.assertEqual(knowledge.read_reference(self.root, explicit)["maintenance"]["status"], "stale")

    def test_supporting_page_routes_to_primary_topic_without_evidence_grade(self):
        guide = "references/core/network/GUIDE.md"
        detail = "references/patterns/network/sync.md"
        self.write(guide, "---\ndescription: 联机同步入口\n---\n# 联机\n权威状态。\n")
        self.write(detail, "# 同步细节\nRPC 初值与 dirty。\n")
        self.write(knowledge.DOCUMENT_ROUTES, json.dumps({"schema_version": 1,
            "supporting_documents": {detail: ["core/network"]}}))
        corpus = knowledge.Corpus(self.root)
        row = next(row for row in corpus.search("dirty")["results"] if row["path"] == detail)
        self.assertEqual(row["role"], "supporting_detail")
        self.assertEqual(row["primary_topics"], [guide])
        topic = corpus.topics("联机")["topics"][0]
        self.assertIn(detail, topic["supporting_documents"])
        self.assertEqual(topic["evidence_grade"], "not_assigned")

    def test_supporting_hit_exposes_primary_candidate_outside_result_limit(self):
        guide = "references/core/network/GUIDE.md"
        detail = "references/patterns/network/sync.md"
        self.write(guide, "---\ndescription: 联机同步入口\n---\n# 联机\n权威状态。\n")
        self.write(detail, "# 同步细节\nRPC 初值与 dirty。\n")
        self.write(knowledge.DOCUMENT_ROUTES, json.dumps({"schema_version": 1,
            "supporting_documents": {detail: ["core/network"]}}))
        result = knowledge.Corpus(self.root).search("dirty", limit=1)
        self.assertEqual([row["path"] for row in result["results"]], [detail])
        self.assertEqual(result["primary_topic_candidates"][0]["path"], guide)
        self.assertNotIn("evidence_grade", result["primary_topic_candidates"][0])

    def test_topics_use_aliases_and_detail_text(self):
        guide = "references/gameplay/state/GUIDE.md"
        detail = "references/patterns/ai/state.md"
        self.write(guide, "# StateGraph 编写\n主流程。\n")
        self.write(detail, "# 状态图\n预测和服务器纠正。\n")
        self.write(knowledge.DOCUMENT_ROUTES, json.dumps({"schema_version": 1,
            "supporting_documents": {detail: ["gameplay/state"]}}))
        corpus = knowledge.Corpus(self.root)
        by_english = corpus.topics("预测")["topics"]
        by_chinese = corpus.topics("状态机 预测")["topics"]
        self.assertEqual([row["path"] for row in by_english], [guide])
        self.assertEqual([row["path"] for row in by_chinese], [guide])

    def test_topics_require_direct_terms_and_apply_limit(self):
        guide = "references/gameplay/state/GUIDE.md"
        self.write(guide, "# StateGraph 编写\n状态图与动作。\n")
        corpus = knowledge.Corpus(self.root)
        self.assertEqual(corpus.topics("不存在词")["topics"], [])
        self.assertEqual(corpus.topics("动作", limit=0)["matched"], 1)
        with self.assertRaises(ValueError):
            corpus.topics("", limit=51)

    def test_invalid_route_does_not_claim_an_owner(self):
        detail = "references/patterns/network/sync.md"
        self.write(detail, "# Sync\nRPC detail.\n")
        self.write(knowledge.DOCUMENT_ROUTES, json.dumps({"schema_version": 1,
            "supporting_documents": {detail: ["core/missing"]}}))
        result = knowledge.Corpus(self.root).search("RPC")
        self.assertEqual(result["scope"]["status"], "partial")
        self.assertEqual(result["scope"]["topic_catalog"]["status"], "unavailable")
        self.assertEqual(result["results"][0]["primary_topics"], [])

    def test_synonym_match_is_not_reported_as_direct_evidence(self):
        self.write("references/art/GUIDE.md", "# 图像 atlas\nTexture conversion.\n")
        result = knowledge.Corpus(self.root).search("贴图")
        self.assertEqual(result["results"][0]["path"], "references/art/GUIDE.md")
        self.assertFalse(result["results"][0]["direct_match"])

    def test_latin_alias_does_not_match_inside_an_unrelated_word(self):
        self.write("references/art/GUIDE.md", "# Build archive\nAsset build output.\n")
        self.write("references/ui/GUIDE.md", "# UI Widget\n界面控件与 HUD。\n")
        rows = knowledge.Corpus(self.root).search("build")["results"]
        self.assertEqual([row["path"] for row in rows], ["references/art/GUIDE.md"])

    def test_temperature_alias_locates_contract_without_inventing_a_direct_match(self):
        self.write("references/components/temperature.md", "# Temperature\nPersistent control ownership.\n")
        row = knowledge.Corpus(self.root).search("恒温")["results"][0]
        self.assertEqual(row["path"], "references/components/temperature.md")
        self.assertFalse(row["direct_match"])

    def test_excluded_trees_are_pruned_before_enumeration_or_reading(self):
        blocked = ["references/mod-notes", "references/knowledge/dst-engineering-kb",
                   "references/art/assets", "references/tools/tests", "references/linked"]
        for directory in blocked:
            self.write(directory + "/secret.md", "secretfixturecode")
        self.write("references/topic/GUIDE.md", "# Ordinary\nordinaryfixturecode\n")
        real_scandir, real_read = os.scandir, Path.read_bytes
        blocked_paths = [self.root / name for name in blocked]

        def guard_scandir(path):
            self.assertNotIn(Path(path), blocked_paths)
            return real_scandir(path)

        def guard_read(path):
            self.assertFalse(any(directory in path.parents for directory in blocked_paths))
            return real_read(path)

        real_link = knowledge.is_link
        with patch.object(knowledge, "is_link", side_effect=lambda p: p.name == "linked" or real_link(p)), \
                patch("os.scandir", side_effect=guard_scandir), patch.object(Path, "read_bytes", guard_read):
            corpus = knowledge.Corpus(self.root)
            self.assertEqual(corpus.search("secretfixturecode")["results"], [])
            self.assertEqual(len(corpus.documents), 2)

    def test_windows_junction_attribute_is_excluded(self):
        with patch.object(Path, "lstat", return_value=SimpleNamespace(st_file_attributes=0x400)), \
                patch.object(Path, "is_symlink", return_value=False):
            self.assertTrue(knowledge.is_link(self.root / "junction"))

    def test_restricted_note_link_does_not_become_a_retrieval_hit(self):
        self.write("references/topic/GUIDE.md", "# Ordinary\n[privatecasefixture](../../mod-notes/private.md)\n")
        self.assertEqual(knowledge.Corpus(self.root).search("privatecasefixture")["results"], [])

    def test_read_rejects_unauthorized_and_parent_paths_before_touching_them(self):
        for path in ["../outside.md", "references/../outside.md", "C:/outside.md", "/outside.md",
                     "references/mod-notes/missing.md", "references/art/assets/missing.md",
                     "references/MOD-NOTES/missing.md", "references/Knowledge/DST-ENGINEERING-KB/INDEX.md",
                     "references/mod-notes./missing.md", "references/mod-notes /missing.md",
                     "references/mod-notes::$INDEX_ALLOCATION/missing.md",
                     "references/knowledge/dst-engineering-kb/README.md", "references/tools/run.py"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                knowledge.read_reference(self.root, path)

    def test_read_rejects_linked_parent(self):
        self.write("references/linked/test.md", "fixture")
        real_link = knowledge.is_link
        with patch.object(knowledge, "is_link", side_effect=lambda p: p.name == "linked" or real_link(p)):
            with self.assertRaises(ValueError):
                knowledge.read_reference(self.root, "references/linked/test.md")

    def test_read_preserves_line_numbers_hash_and_prefab_names(self):
        path = self.write(knowledge.NAME_TABLE, '{\n  "acorn": "桦栗果"\n}\n')
        row = knowledge.Corpus(self.root).search("桦栗果")["results"][0]
        self.assertEqual(row["path"], knowledge.NAME_TABLE)
        result = knowledge.read_reference(self.root, row["path"], 2, 1)
        self.assertEqual(result["lines"], [{"number": 2, "text": '  "acorn": "桦栗果"'}])
        self.assertEqual(result["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_unreadable_file_reports_partial_scope(self):
        self.write("references/topic/GUIDE.md", "# fixture")
        real_read = Path.read_bytes

        def guarded(path):
            if path.name == "GUIDE.md":
                raise PermissionError("fixture read denied")
            return real_read(path)

        with patch.object(Path, "read_bytes", guarded):
            scope = knowledge.Corpus(self.root).scope()
        self.assertEqual(scope["status"], "partial")
        self.assertEqual(scope["read_errors"][0]["path"], "references/topic/GUIDE.md")

    def test_missing_kb_keeps_documents_and_explicit_error(self):
        self.write("references/topic/GUIDE.md", "# unique_fixture_topic")
        config = self.write("fixture.json", json.dumps({"kb_path": "missing", "index_path": "cache/index.sqlite3"}))
        with patch.dict(os.environ, {"DST_KB_PATH": "", "DST_KB_INDEX": "", "DST_KB_CONFIG": ""}):
            result = knowledge.lookup("unique_fixture_topic", config=config, root=self.root)
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["documents"]["results"])
        self.assertEqual(result["engineering_kb"]["status"], "unavailable")
        self.assertIn("error", result["engineering_kb"])

    def test_no_match_and_invalid_query_are_not_success_evidence(self):
        corpus = knowledge.Corpus(self.root)
        self.assertTrue(corpus.search("qzx_unlisted_98277")["knowledge_gap"])
        for query, limit in [("", 5), ("x" * 4001, 5), ("fixture", 0), ("fixture", 11)]:
            with self.subTest(query=query[:10], limit=limit), self.assertRaises(ValueError):
                corpus.search(query, limit)


class RealReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = knowledge.Corpus()

    def test_real_tasks_reach_relevant_existing_topics(self):
        cases = [
            ("远端客户端 RPC 校验 HUD 初始同步", "references/core/dst-networking-rpc/GUIDE.md"),
            ("新增独立锅料理 调味变体 食谱", "references/engineering/dst-mod-engineering/cooker-dishes.md"),
            ("OnSave OnLoad 存档 数据迁移", "references/core/dst-persistence-migration/GUIDE.md"),
            ("贴图 alpha 256 64 透明", "references/world-ui-assets/dst-texture-style/GUIDE.md"),
            ("重连后效果残留 任务监听清理", "references/core/dst-events-tasks-lifecycle/GUIDE.md"),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                result = self.corpus.search(query, limit=5)
                self.assertIn(expected, [row["path"] for row in result["results"]])

    def test_current_topic_routes_cover_all_legacy_patterns(self):
        catalog = self.corpus.topics()
        self.assertEqual(catalog["routes_status"], "available")
        self.assertEqual(catalog["total"], 50)
        routed = self.corpus.document_routes["routes"]
        pattern_paths = {doc.path for doc in self.corpus.documents
                         if doc.path.startswith("references/patterns/")}
        self.assertEqual(pattern_paths - routed.keys(), set())
        self.assertTrue(all(row["description"] for row in catalog["topics"]))

    def test_real_cross_language_topic_queries_reach_guides(self):
        cases = [
            ("状态机 预测", "references/gameplay/dst-stategraph-authoring/GUIDE.md"),
            ("皮肤 切换", "references/world-ui-assets/dst-skins-symbol-overrides/GUIDE.md"),
            ("Lua Hook", "references/core/dst-hooking-compatibility/GUIDE.md"),
            ("DMT 安装", "references/core/dst-mod-scaffolding/GUIDE.md"),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                paths = [row["path"] for row in self.corpus.topics(query)["topics"]]
                self.assertIn(expected, paths)

    def test_real_supporting_hits_offer_primary_topic_candidates(self):
        cases = [
            ("状态机 预测", "references/gameplay/dst-stategraph-authoring/GUIDE.md"),
            ("皮肤 切换", "references/world-ui-assets/dst-skins-symbol-overrides/GUIDE.md"),
            ("Lua Hook", "references/core/dst-hooking-compatibility/GUIDE.md"),
            ("DMT 安装", "references/core/dst-mod-scaffolding/GUIDE.md"),
        ]
        for query, expected in cases:
            with self.subTest(query=query):
                result = self.corpus.search(query, limit=5)
                paths = {row["path"] for row in result["results"]}
                paths.update(row["path"] for row in result["primary_topic_candidates"])
                self.assertIn(expected, paths)

    def test_real_item_name_reaches_original_name_table(self):
        rows = self.corpus.search("桦栗果", limit=5)["results"]
        self.assertIn(knowledge.NAME_TABLE, [row["path"] for row in rows])

    def test_real_internal_attack_api_reaches_combat_contract(self):
        result = self.corpus.search("GetAttacked_Internal", limit=3)
        paths = {row["path"] for row in result["results"]}
        self.assertIn("references/components/combat/combat.md", paths)
        self.assertIn("references/gameplay/dst-combat-weapons-projectiles/GUIDE.md", paths)
        self.assertTrue(all("GetAttacked_Internal" in row["snippet"] for row in result["results"]))

    def test_current_component_queries_reach_details_and_primary_topics(self):
        cases = [
            ("物品温度", "references/components/system/inventoryitemtemperature.md",
             "references/gameplay/dst-inventory-equipment-containers/GUIDE.md"),
            ("定向使用物品", "references/components/items/useabletargeteditem.md",
             "references/core/dst-action-authoring/GUIDE.md"),
            ("deflectable", "references/components/combat/deflectable.md",
             "references/gameplay/dst-combat-weapons-projectiles/GUIDE.md"),
        ]
        for query, detail, guide in cases:
            with self.subTest(query=query):
                result = self.corpus.search(query, limit=3)
                row = next(row for row in result["results"] if row["path"] == detail)
                self.assertEqual(row["role"], "supporting_detail")
                self.assertIn(guide, row["primary_topics"])
                candidates = {row["path"] for row in result["results"] + result["primary_topic_candidates"]}
                self.assertIn(guide, candidates)

    def test_unknown_symbol_returns_no_match(self):
        self.assertEqual(self.corpus.search("qzx_unlisted_98277")["results"], [])

    def test_powershell_entry_preserves_chinese_read_and_legacy_command(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if shell is None:
            self.skipTest("PowerShell unavailable")
        entry = knowledge.SKILL_ROOT / "references/tools/engineering/run.ps1"
        read = subprocess.run([shell, "-NoProfile", "-File", str(entry), "knowledge", "read",
                               knowledge.NAME_TABLE, "--start", "2", "--count", "1"],
                              capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertIn("灰烬", json.loads(read.stdout)["lines"][0]["text"])
        help_result = subprocess.run([sys.executable, "-B", str(TOOLS / "dst_kb_cli.py"), "--help"],
                                     capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("serve", help_result.stdout)
        self.assertIn("lookup", help_result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
