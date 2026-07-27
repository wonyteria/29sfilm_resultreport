from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TemplateChoice:
    filename: str
    event_type: str
    slides: int
    score: int
    reasons: tuple[str, ...]


def _event_type(filename: str) -> str:
    return "29역숏폼왕" if "숏폼왕" in filename else "29초영화제"


def recommend_templates(catalog_path: str | Path, event_type: str, selected_keys: set[str]) -> list[TemplateChoice]:
    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    choices: list[TemplateChoice] = []
    for report in catalog["reports"]:
        report_type = _event_type(report["file"])
        counts = Counter(report.get("module_counts", {}))
        present = {key for key, count in counts.items() if count and key != "unclassified"}
        overlap = len(selected_keys & present)
        missing = len(selected_keys - present)
        type_bonus = 100 if report_type == event_type else -100
        score = type_bonus + overlap * 5 - missing * 3
        reasons = (f"선택 모듈 {overlap}개 일치", f"없는 모듈 {missing}개", f"기존 {report['slides']}쪽")
        choices.append(TemplateChoice(report["file"], report_type, report["slides"], score, reasons))
    return sorted(choices, key=lambda item: item.score, reverse=True)
