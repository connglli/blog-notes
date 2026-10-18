#!/usr/bin/env python3
"""Check summary structure against TEMPLATE.md, without third-party dependencies.

By default, inspect only root-level Markdown added, modified, copied, or renamed
in the staged changes, using index contents and the index version of TEMPLATE.md.
--no-staged explicitly checks the working tree, including untracked drafts.
Technical accuracy and prose quality still require human/source review.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit, parse_qs


NON_SUMMARIES = {"AGENTS.md", "README.md", "TEMPLATE.md"}
FIELD = re.compile(r"^\*\*([^*]+):\*\*\s*(.*?)\s*$")
HEADING = re.compile(r"^## (.+)$")
CONCEPT = re.compile(r"^\*\*\[(\d+)\]\s+.+?\*\*")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


@dataclass(frozen=True)
class Schema:
    fields: tuple[str, ...]
    sections: tuple[str, ...]

    @classmethod
    def from_template(cls, text: str) -> Schema:
        marker = "<!-- Optional resources -->"
        if marker not in text:
            raise ValueError("TEMPLATE.md needs its Optional resources marker")
        required = text.split(marker, 1)[0]
        fields = tuple(m.group(1) for line in required.splitlines() if (m := FIELD.match(line)))
        sections = tuple(m.group(1) for line in text.splitlines() if (m := HEADING.match(line)))
        if not fields or not sections or "Link" not in fields:
            raise ValueError("TEMPLATE.md must define required metadata and sections")
        if len(set(fields)) != len(fields) or len(set(sections)) != len(sections):
            raise ValueError("TEMPLATE.md contains duplicate fields or sections")
        return cls(fields, sections)


def visible_lines(text: str) -> tuple[list[str], list[str]]:
    """Blank fenced code while retaining line numbers for diagnostics."""
    visible: list[str] = []
    errors: list[str] = []
    opened: tuple[str, int, int] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if opened:
            visible.append("")
            if match and match[1][0] == opened[0] and len(match[1]) >= opened[1] and not match[2].strip():
                opened = None
        elif match:
            opened = (match[1][0], len(match[1]), number)
            visible.append("")
        else:
            visible.append(line)
    if opened:
        errors.append(f"line {opened[2]}: unclosed code fence")
    return visible, errors


def without_inline_code(text: str) -> str:
    return re.sub(r"(`+).*?\1", lambda m: " " * len(m[0]), text)


def is_pdf_url(url: str) -> bool:
    url = unquote(url.strip("<> \t\r\n").rstrip(".,;"))
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    path = parts.path.lower().rstrip(")")
    if re.search(r"\.pdf(?:$|/)", path) or re.search(r"(?:^|/)(?:e?pdf)(?:/|$)", path):
        return True
    return any(value.lower() == "pdf" for key, values in parse_qs(parts.query).items()
               if key.lower() in {"format", "output", "type"} for value in values)


def pdf_errors(text: str) -> list[str]:
    lines, _ = visible_lines(text)
    errors = []
    for number, line in enumerate(lines, 1):
        line = without_inline_code(line)
        # Includes bare/autolink URLs, Markdown destinations, reference links,
        # and HTML href/src values. Relative PDF links are covered as well.
        targets = re.findall(r"https?://[^\s<>\"\]]+", line)
        targets += [angle or plain for angle, plain in re.findall(r"\]\(\s*(?:<([^>]+)>|([^\s)]+))", line)]
        targets += [angle or plain for angle, plain in re.findall(r"^\s*\[[^]]+\]:\s*(?:<([^>]+)>|([^\s]+))", line)]
        targets += re.findall(r"(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", line, re.I)
        if any(is_pdf_url(target) for target in targets):
            errors.append(f"line {number}: PDF links are forbidden; use a publication landing page")
    return errors


def validate(text: str, schema: Schema) -> list[str]:
    lines = text.splitlines()
    visible, errors = visible_lines(text)
    errors += pdf_errors(text)
    if not lines or not re.fullmatch(r"# \S.*", lines[0]):
        errors.append("line 1: expected a nonempty level-1 work title")
    titles = [i for i, line in enumerate(visible) if line.startswith("# ")]
    if titles != [0]:
        errors.append("use exactly one level-1 heading, on the first line")
    headings = [(i, m[1]) for i, line in enumerate(visible) if (m := HEADING.match(line))]
    actual = [heading for _, heading in headings]
    normalized = ["Illustrative example" if h.startswith("Illustrative example: ") else h for h in actual]
    if normalized != list(schema.sections):
        errors.append("sections must follow TEMPLATE.md: " + ", ".join(schema.sections))
    first_section = headings[0][0] if headings else len(lines)
    metadata = []
    for i in range(1, first_section):
        if not visible[i].strip():
            continue
        match = FIELD.match(visible[i])
        if not match:
            errors.append(f"line {i + 1}: metadata must be a single **Label:** value line")
            continue
        label, value = match.groups()
        metadata.append((label, value, i))
        if not value:
            errors.append(f"line {i + 1}: {label} must not be empty")
        if i == 0 or lines[i - 1].strip() or i + 1 >= len(lines) or lines[i + 1].strip():
            errors.append(f"line {i + 1}: separate metadata fields with blank lines")
        if "pdf" in label.lower() or label.lower() in {"arxiv", "paper"}:
            errors.append(f"line {i + 1}: keep the work's publication URL only in Link")
    labels = [label for label, _, _ in metadata]
    if labels[:len(schema.fields)] != list(schema.fields):
        errors.append("required metadata order: " + ", ".join(schema.fields))
    for label in schema.fields:
        if labels.count(label) != 1:
            errors.append(f"expected exactly one {label} field")
    for label, value, i in metadata:
        if label == "Link":
            if not re.fullmatch(r"https?://[^\s<>\[\]()]+", value):
                errors.append(f"line {i + 1}: Link must contain one bare publication URL, not a Markdown link")
            else:
                try:
                    parts = urlsplit(value)
                    if not parts.hostname or parts.hostname.endswith(".example"):
                        raise ValueError("placeholder or missing hostname")
                except ValueError:
                    errors.append(f"line {i + 1}: invalid publication URL")

    for i, line in enumerate(visible):
        if re.search(r"\{\{.+?\}\}", line):
            errors.append(f"line {i + 1}: replace the template placeholder")
        if re.search(r"<br\s*/?>", line, re.I):
            errors.append(f"line {i + 1}: use blank lines rather than HTML line breaks")
        if re.search("[\u2013\u2014]", line):
            errors.append(f"line {i + 1}: replace em/en dashes with plain punctuation")
        if re.match(r"\s*[-+] ", line):
            errors.append(f"line {i + 1}: use * for Markdown bullets")
        if re.match(r"^#{3,} ", line):
            errors.append(f"line {i + 1}: use short bold phase titles, not extra headings")
    for index, (start, heading) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(lines)
        body = "\n".join(lines[start + 1:end]).strip()
        if not re.sub(r"<!--.*?-->", "", body, flags=re.S).strip():
            errors.append(f"line {start + 1}: {heading} must not be empty")
        if heading in {"Key insight", "Basic idea"} and "\n" in body:
            errors.append(f"line {start + 1}: {heading} must be one physical paragraph line")
        if start == 0 or lines[start - 1].strip() or start + 1 >= len(lines) or lines[start + 1].strip():
            errors.append(f"line {start + 1}: separate headings and content with blank lines")

    concept_section = next((i for i, h in headings if h == "Concepts and terms"), len(lines))
    concepts = [(i, int(m[1])) for i, line in enumerate(visible)
                if i > concept_section and (m := CONCEPT.match(line))]
    numbers = [n for _, n in concepts]
    if not numbers or numbers != list(range(1, len(numbers) + 1)):
        errors.append("concept entries must use **[1] Name.**, **[2] Name.**, ... without gaps or duplicates")
    for offset, (i, number) in enumerate(concepts):
        end = concepts[offset + 1][0] if offset + 1 < len(concepts) else len(lines)
        description = CONCEPT.sub("", lines[i], count=1) + "\n" + "\n".join(lines[i + 1:end])
        if not description.strip():
            errors.append(f"line {i + 1}: concept [{number}] has no explanation")
    prose = without_inline_code("\n".join(visible))
    for match in re.finditer(r"(?<!\w)\[(\d+)\](?!\()", prose):
        if int(match[1]) not in numbers:
            errors.append(f"undefined concept reference [{match[1]}]")
    return list(dict.fromkeys(errors))


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def check_repository(root: Path, staged: bool = True) -> tuple[list[str], int]:
    if staged:
        paths = [p.decode("utf-8") for p in git(
            root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"
        ).split(b"\0") if p]
        def read(path: str) -> str:
            return git(root, "show", ":" + path).decode("utf-8")
    else:
        paths = [p.name for p in root.glob("*.md")]
        def read(path: str) -> str:
            return (root / path).read_text(encoding="utf-8")
    paths = sorted({path for path in paths
                    if PurePosixPath(path).parent == PurePosixPath(".") and path.endswith(".md")})
    if not paths:
        return [], 0
    try:
        template = read("TEMPLATE.md")
    except ValueError:
        return ["TEMPLATE.md: stage the template before committing summary-format changes"], 0
    schema = Schema.from_template(template)
    errors = []
    count = 0
    for path in paths:
        text = read(path)
        if path in NON_SUMMARIES:
            issues = pdf_errors(text)
        else:
            count += 1
            issues = validate(text, schema)
        errors.extend(f"{path}: {issue}" for issue in issues)
    return errors, count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action=argparse.BooleanOptionalAction, default=True,
                        help="validate only staged changes using index contents (default); --no-staged checks the working tree")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        errors, count = check_repository(args.root.resolve(), args.staged)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"Summary check failed: {error}", file=sys.stderr)
        return 1
    if errors:
        print("Summary format check failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    location = "staged changes" if args.staged else "working tree"
    print(f"Summary format check passed: {count} summaries ({location}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
