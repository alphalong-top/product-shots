import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"


class SkillIntegrityTests(unittest.TestCase):
    def test_skill_frontmatter_has_matching_name_and_description(self):
        skill_files = sorted(SKILLS_ROOT.glob("*/SKILL.md"))
        self.assertTrue(skill_files)
        for skill_file in skill_files:
            with self.subTest(skill=skill_file.parent.name):
                text = skill_file.read_text()
                self.assertTrue(text.startswith("---\n"))
                closing = text.find("\n---\n", 4)
                self.assertGreater(closing, 0)
                frontmatter = text[4:closing]
                name_match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", frontmatter, re.MULTILINE)
                description_match = re.search(r"^description:\s*.+", frontmatter, re.MULTILINE)
                self.assertIsNotNone(name_match)
                self.assertEqual(name_match.group(1).strip(), skill_file.parent.name)
                self.assertIsNotNone(description_match)

    def test_internal_reference_paths_exist(self):
        pattern = re.compile(
            r"(?:(?:\.\./)?product-shots-[a-z-]+/)?"
            r"(?:references|scripts)/[A-Za-z0-9_.-]+(?:\.md|\.py|\.sh)"
        )
        for skill_dir in sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir()):
            for markdown_file in skill_dir.rglob("*.md"):
                for relative in pattern.findall(markdown_file.read_text()):
                    with self.subTest(source=markdown_file, target=relative):
                        if relative.startswith("../"):
                            target = skill_dir / relative
                        elif relative.startswith("product-shots-"):
                            target = SKILLS_ROOT / relative
                        else:
                            target = skill_dir / relative
                        self.assertTrue(target.resolve().is_file())


if __name__ == "__main__":
    unittest.main()
