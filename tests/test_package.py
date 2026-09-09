"""Checks the release contract and self-contained copied skill packages."""
import ast
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [ROOT / "skills" / "meta-agent" / name for name in ("use-claude", "use-codex")]


class PackageTests(unittest.TestCase):
    def test_release_versions_and_entrypoints_match(self):
        normalized = []
        for skill in SKILLS:
            entry = (skill / "SKILL.md").read_text()
            version = re.search(r'^  version: "(\d+\.\d+\.\d+)"$', entry, re.M).group(1)
            frontmatter = entry.split("---", 2)[1]
            self.assertIn(f"name: {skill.name}\n", frontmatter)
            description = re.search(r"^description: (.+)$", frontmatter, re.M).group(1)
            self.assertLessEqual(len(description), 1024)
            normalized.append(entry.replace(f'  version: "{version}"', '  version: "VERSION"').replace("Claude Code", "Provider").replace("Claude", "Provider")
                              .replace("Codex", "Provider").replace("claude", "provider").replace("codex", "provider"))
            module = ast.parse((skill / "scripts/run_worker.py").read_text())
            constants = {target.id: ast.literal_eval(node.value)
                         for node in module.body if isinstance(node, ast.Assign)
                         for target in node.targets if isinstance(target, ast.Name) and target.id == "SKILL_VERSION"}
            self.assertEqual(constants["SKILL_VERSION"], version)
        self.assertEqual(*normalized)

    def test_copied_resources_remain_identical(self):
        for relative in ("assets/result.schema.json", "assets/worker-contract.md", "scripts/run_worker.py",
                         "scripts/jobs.py", "scripts/launch_profiles.py", "references/runner.md", "references/jobs.md"):
            with self.subTest(path=relative):
                contents = [(skill / relative).read_text() for skill in SKILLS]
                if relative == "scripts/run_worker.py":
                    contents = [re.sub(r'^SKILL_VERSION = "[^"\n]+"$', 'SKILL_VERSION = "VERSION"',
                                       content, flags=re.M) for content in contents]
                self.assertEqual(*contents)
        layouts = [sorted(str(p.relative_to(skill)) for p in skill.rglob("*")
                          if p.is_file() and "__pycache__" not in p.parts) for skill in SKILLS]
        self.assertEqual(*layouts)

    def test_local_links_resolve_within_skill(self):
        for skill in SKILLS:
            for path in skill.rglob("*.md"):
                for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                    if "://" in link or link.startswith("#"):
                        continue
                    target = (path.parent / link.split("#")[0]).resolve()
                    self.assertTrue(target.exists(), f"{path}: {link}")
                    self.assertIn(skill.resolve(), [target, *target.parents], f"nonportable reference {link}")

    def test_handoff_protocol_shape(self):
        schema = json.loads((SKILLS[0] / "assets/result.schema.json").read_text())
        # Claude Code 2.1.263 rejects the 2020-12 dialect before dispatch.
        self.assertEqual(schema["$schema"], "http://json-schema.org/draft-07/schema#")
        self.assertEqual(schema["$id"], "urn:jvloo:agent-skills:worker-result:1")
        self.assertEqual(schema["type"], "object")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(set(schema["properties"]), set(schema["required"]))
        self.assertEqual(schema["properties"]["status"]["enum"], ["completed", "blocked", "failed"])


if __name__ == "__main__":
    unittest.main()
