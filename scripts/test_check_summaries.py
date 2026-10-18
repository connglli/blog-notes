"""Regression tests, including isolated Git repositories for staged validation."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_summaries import Schema, check_repository, is_pdf_url, pdf_errors, validate


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "TEMPLATE.md").read_text(encoding="utf-8")
SCHEMA = Schema.from_template(TEMPLATE)
VALID = """# Example work

**Summary by:** Original writer and Editor

**Author:** Work author

**Source:** Conference 2026

**Link:** https://doi.org/10.1234/example

**Code:** [Repository](https://github.com/example/project)

**Artifact:** [Artifact](https://doi.org/10.5281/zenodo.12345)

## Key insight

A concise central idea.

## Basic idea

The mechanism uses a concept [1].

## Illustrative example

**Setup.** An original example.

## Concepts and terms

**[1] Concept.** A complete explanation.
"""


class ValidationTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate(VALID, SCHEMA), [])

    def test_schema_is_read_from_template(self):
        schema = Schema.from_template(TEMPLATE.replace("**Author:**", "**Authors:**"))
        self.assertIn("Authors", schema.fields)
        self.assertTrue(validate(VALID, schema))
        self.assertEqual(validate(VALID.replace("**Author:**", "**Authors:**"), schema), [])

    def test_hidden_publication_link(self):
        bad = VALID.replace("**Link:** https://doi.org/10.1234/example", "**Link:** [Paper](https://doi.org/10.1234/example)")
        self.assertTrue(any("bare publication URL" in error for error in validate(bad, SCHEMA)))

    def test_two_publication_urls(self):
        bad = VALID.replace("**Link:** https://doi.org/10.1234/example", "**Link:** https://doi.org/10.1234/example https://example.org/other")
        self.assertTrue(validate(bad, SCHEMA))

    def test_pdf_forms(self):
        for url in ["https://example.org/paper.PDF", "https://example.org/paper%2Epdf?download=1",
                    "https://arxiv.org/pdf/1234.56789", "https://openreview.net/pdf?id=abc",
                    "https://dl.acm.org/doi/epdf/10.1234/abc", "docs/report.pdf",
                    "https://example.org/article?format=pdf"]:
            with self.subTest(url=url):
                self.assertTrue(is_pdf_url(url))
                self.assertTrue(pdf_errors(f"[Download]({url})"))
        for line in ['[Download](<docs/my report.pdf>)', '[source]: <docs/my report.pdf>',
                     '<a href="docs/report.pdf">Download</a>', 'https://example.org/report.pdf']:
            with self.subTest(line=line):
                self.assertTrue(pdf_errors(line))

    def test_non_pdf_resource_links(self):
        self.assertFalse(pdf_errors("[Artifact](https://doi.org/10.5281/zenodo.12345)"))
        self.assertFalse(pdf_errors("[Documentation](https://example.org/pdf-tools.html)"))

    def test_code_is_not_prose(self):
        code = '\n```text\n## Fake section\n[99] data[0]\nhttps://example.org/file.pdf\n```\n'
        text = VALID.replace("**Setup.** An original example.\n", "**Setup.** An original example.\n" + code)
        self.assertEqual(validate(text, SCHEMA), [])
        self.assertEqual(validate(VALID.replace("A complete explanation.", "Use `data[99]`."), SCHEMA), [])

    def test_unclosed_fence(self):
        self.assertTrue(any("unclosed" in error for error in validate(VALID + "\n```python\nx = 1\n", SCHEMA)))

    def test_missing_and_misordered_metadata(self):
        for bad in [VALID.replace("**Author:** Work author\n\n", ""),
                    VALID.replace("**Author:** Work author", "**Author:**"),
                    VALID.replace("**Summary by:** Original writer and Editor", "**Author:** Work author")]:
            with self.subTest(text=bad):
                self.assertTrue(validate(bad, SCHEMA))

    def test_sections_and_spacing(self):
        self.assertTrue(validate(VALID.replace("## Basic idea", "## Other"), SCHEMA))
        self.assertTrue(validate(VALID.replace("## Basic idea\n\n", "## Basic idea\n"), SCHEMA))
        self.assertTrue(validate(VALID.replace("A concise central idea.", "A sentence.\nAnother line."), SCHEMA))
        self.assertEqual(validate(VALID.replace("## Illustrative example", "## Illustrative example: a smaller case"), SCHEMA), [])

    def test_concepts_and_references(self):
        self.assertTrue(validate(VALID.replace("**[1] Concept.", "**[2] Concept."), SCHEMA))
        self.assertTrue(validate(VALID.replace("concept [1]", "concept [2]"), SCHEMA))
        self.assertTrue(validate(VALID.replace("A complete explanation.", "See [99]."), SCHEMA))
        self.assertTrue(validate(VALID.replace("A complete explanation.", ""), SCHEMA))

    def test_placeholders_and_legacy_breaks(self):
        self.assertTrue(validate(VALID.replace("Example work", "{{Work title}}"), SCHEMA))
        self.assertTrue(validate(VALID.replace("Work author", "Work author<br/>"), SCHEMA))


class StagedTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="summary-hook-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.run_git("init", "-q")
        self.run_git("config", "--local", "core.hooksPath", ".githooks")
        self.run_git("config", "--local", "user.name", "Summary test")
        self.run_git("config", "--local", "user.email", "summary-test@example.invalid")
        self.write("TEMPLATE.md", TEMPLATE)
        self.write("example.md", VALID)
        self.run_git("add", "TEMPLATE.md", "example.md")

    def run_git(self, *args, check=True):
        return subprocess.run(["git", "-C", str(self.root), *args], env=self.env,
                              check=check, capture_output=True, text=True)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit_fixture(self):
        self.run_git("-c", "commit.gpgsign=false", "commit", "-m", "fixture baseline")

    def test_valid_index_ignores_invalid_working_copy_and_template(self):
        self.write("example.md", "broken working copy\n")
        self.write("TEMPLATE.md", "broken working template\n")
        self.write("untracked.md", "broken untracked draft\n")
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_cli_defaults_to_staged_changes(self):
        self.write("example.md", "broken working copy\n")
        command = [sys.executable, str(ROOT / "scripts/check_summaries.py"), "--root", str(self.root)]
        for flags in [[], ["--staged"]]:
            with self.subTest(flags=flags):
                result = subprocess.run(command + flags, env=self.env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("1 summaries (staged changes)", result.stdout)
        result = subprocess.run(command + ["--no-staged"], env=self.env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("example.md", result.stderr)

    def test_unchanged_index_files_are_not_checked(self):
        self.write("legacy.md", "invalid but unchanged committed summary\n")
        self.write("README.md", "[Download](https://example.org/work.pdf)\n")
        self.run_git("add", "legacy.md", "README.md")
        self.commit_fixture()
        self.write("example.md", VALID.replace("# Example work", "# Updated work"))
        self.run_git("add", "example.md")
        self.assertEqual(check_repository(self.root), ([], 1))

    def test_no_staged_changes_checks_nothing(self):
        self.commit_fixture()
        self.write("example.md", "broken unstaged change\n")
        self.write("untracked.md", "broken untracked draft\n")
        self.assertEqual(check_repository(self.root), ([], 0))

    def test_template_change_does_not_check_unchanged_summaries(self):
        self.commit_fixture()
        self.write("TEMPLATE.md", TEMPLATE.replace("**Author:**", "**Authors:**"))
        self.run_git("add", "TEMPLATE.md")
        self.assertEqual(check_repository(self.root), ([], 0))

    def test_no_staged_markdown_does_not_require_template(self):
        self.run_git("rm", "--cached", "TEMPLATE.md", "example.md")
        self.write("notes.txt", "not Markdown\n")
        self.run_git("add", "notes.txt")
        self.assertEqual(check_repository(self.root), ([], 0))

    def test_working_fix_cannot_hide_invalid_staged_copy(self):
        self.commit_fixture()
        self.write("example.md", VALID.replace("**Link:** https://doi.org/10.1234/example", "**Link:** [Paper](https://doi.org/10.1234/example)"))
        self.run_git("add", "example.md")
        self.write("example.md", VALID)
        errors, _ = check_repository(self.root, staged=True)
        self.assertTrue(any("bare publication URL" in error for error in errors))

    def test_staged_rename_and_deletion(self):
        self.commit_fixture()
        self.run_git("mv", "example.md", "renamed summary.md")
        self.assertEqual(check_repository(self.root, staged=True), ([], 1))
        self.commit_fixture()
        self.run_git("rm", "--cached", "renamed summary.md")
        self.assertEqual(check_repository(self.root, staged=True), ([], 0))

    def test_non_summary_exemptions_still_forbid_pdf_links(self):
        self.write("paper.md", "# Reading list\n\nA bibliography, not a summary.\n")
        self.run_git("add", "paper.md")
        self.assertEqual(check_repository(self.root, staged=True), ([], 1))
        self.write("README.md", "# Project\n\n[Download](https://example.org/work.pdf)\n")
        self.run_git("add", "README.md")
        errors, _ = check_repository(self.root, staged=True)
        self.assertTrue(any("README.md" in error and "PDF links" in error for error in errors))

    def test_missing_staged_template_is_an_error(self):
        self.run_git("rm", "--cached", "TEMPLATE.md")
        errors, _ = check_repository(self.root, staged=True)
        self.assertTrue(any("stage the template" in error for error in errors))

    def test_real_hook_blocks_invalid_commit_and_accepts_valid_commit(self):
        self.write("scripts/check_summaries.py", (ROOT / "scripts/check_summaries.py").read_text())
        self.write(".githooks/pre-commit", (ROOT / ".githooks/pre-commit").read_text())
        (self.root / ".githooks/pre-commit").chmod(0o755)
        self.write("example.md", VALID.replace("**Link:** https://doi.org/10.1234/example", "**Link:** https://example.org/work.pdf"))
        self.run_git("add", "example.md")
        rejected = self.run_git("-c", "commit.gpgsign=false", "commit", "-m", "invalid fixture", check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("PDF links", rejected.stderr)
        self.write("example.md", VALID)
        self.run_git("add", "example.md")
        accepted = self.run_git("-c", "commit.gpgsign=false", "commit", "-m", "valid fixture", check=False)
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)


if __name__ == "__main__":
    unittest.main()
