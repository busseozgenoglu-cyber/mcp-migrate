"""Keep README's headline ``check`` transcript aligned with real CLI output."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from mcp_migrate import __version__
from mcp_migrate.cli import main

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
FIXTURE = ROOT / "tests" / "fixtures" / "fixer_roundtrip"


def _headline_transcript(readme: str) -> str:
    section = readme.split("## `mcp-migrate check`", 1)[1]
    return section.split("```", 2)[1]


def test_headline_check_transcript_matches_cli(capsys):
    exit_code = main(["check", str(FIXTURE), "--json"])
    data = json.loads(capsys.readouterr().out)
    assert exit_code == 1

    readme = README.read_text(encoding="utf-8")
    transcript = _headline_transcript(readme)

    assert f"mcp-migrate v{data['version']}  ->  fixer_roundtrip" in transcript

    finding_counts = Counter(
        (finding["severity"], finding["rule"])
        for finding in data["findings"]
    )
    for (severity, rule), count in finding_counts.items():
        rows = re.findall(rf"(?m)^{severity}\s+{rule}\s+", transcript)
        assert len(rows) == count, (
            f"README lists {len(rows)} {severity} {rule} row(s); CLI reports {count}"
        )

    counts = data["counts"]
    summary = (
        f"Grade {data['grade']} ({data['score']}/100)  "
        f"{counts['breaking']} breaking, {counts['deprecated']} deprecated, "
        f"{counts['advisory']} advisory"
    )
    assert summary in transcript


def test_readme_cli_banners_match_package_version():
    readme = README.read_text(encoding="utf-8")
    versions = re.findall(r"mcp-migrate v(\d+\.\d+\.\d+)\s+->", readme)
    assert versions
    assert set(versions) == {__version__}
