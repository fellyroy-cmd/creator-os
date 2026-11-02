"""Check that every Creator OS skill is well-formed.

Run: python scripts/validate.py
Exits with code 1 (and a list of problems) if anything is wrong, so CI can block a broken pull request.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def read_frontmatter(text):
    """Return the key: value pairs between the opening and closing '---' lines, or None if missing."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_skill(folder):
    problems = []
    skill_file = folder / "SKILL.md"
    if not skill_file.exists():
        return [f"{folder.name}: missing SKILL.md"]

    text = skill_file.read_text(encoding="utf-8").replace("\r\n", "\n")
    fields = read_frontmatter(text)
    if fields is None:
        return [f"{folder.name}: SKILL.md must start with a '---' frontmatter block"]

    name = fields.get("name", "")
    if name != folder.name:
        problems.append(f"{folder.name}: frontmatter name '{name}' must match the folder name")
    if not NAME_RE.match(folder.name):
        problems.append(f"{folder.name}: folder name must be lowercase words joined by hyphens")

    description = fields.get("description", "")
    if len(description) < 40:
        problems.append(f"{folder.name}: description is missing or too short (say what it does and when to use it)")

    # The house rule: every skill except setup personalises its output from the creator profile.
    if folder.name != "setup" and "creator/profile.md" not in text:
        problems.append(f"{folder.name}: should read creator/profile.md in its first step")

    # Every relative link in the skill must point to a file that exists.
    # Code blocks are skipped: they hold output templates like [Source](url), not real links.
    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for link in re.findall(r"\]\(([^)#]+)\)", prose):
        if "://" in link:
            continue
        if not (folder / link).exists():
            problems.append(f"{folder.name}: broken link to '{link}'")

    return problems


def check_manifests():
    problems = []
    for name in ("plugin.json", "marketplace.json"):
        path = ROOT / ".claude-plugin" / name
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            problems.append(f".claude-plugin/{name} is missing")
        except json.JSONDecodeError as err:
            problems.append(f".claude-plugin/{name} is not valid JSON: {err}")
    return problems


def main():
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    problems = check_manifests()
    for folder in skills:
        problems += check_skill(folder)

    if problems:
        print(f"{len(problems)} problem(s) found:")
        for problem in problems:
            print(f"  - {problem}")
        sys.exit(1)
    print(f"All good: {len(skills)} skills checked.")


if __name__ == "__main__":
    main()
