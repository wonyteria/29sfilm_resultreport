from __future__ import annotations

from dataclasses import dataclass

from .page_catalog import MODULES, PageModule
from .scanner import ScanResult


@dataclass
class PageDecision:
    key: str
    section: str
    label: str
    mode: str
    decision: str
    evidence_count: int
    reason: str


def _evidence(module: PageModule, text: str) -> list[str]:
    return [hint for hint in module.source_hints if hint.lower() in text]


def build_report_plan(scan: ScanResult, event_type: str) -> list[PageDecision]:
    text = " ".join(scan.path_index).lower()
    decisions: list[PageDecision] = []
    child_included: dict[str, bool] = {}

    for module in MODULES:
        if module.key.startswith("section_"):
            continue
        hits = _evidence(module, text)
        if module.key in {"cover", "index", "closing"}:
            decision, reason = "자동 포함", "모든 보고서의 공통 페이지입니다."
        elif module.key == "summary":
            decision, reason = "자동 포함", "확정 데이터로 총평 초안을 만들고 담당자가 승인합니다."
        elif module.key in {"overview", "submission", "award_list"}:
            decision = "자동 포함"
            reason = "필수 페이지입니다." if hits else "필수 페이지이며 자료 또는 직접 입력이 필요합니다."
        elif module.key.startswith("ceremony") and event_type == "29역숏폼왕" and not hits:
            decision, reason = "추가 여부 확인", "29역숏폼왕에서는 시상식이 선택 사항입니다."
        elif hits:
            decision = "반복 생성" if module.mode == "repeat" else "자동 포함"
            reason = f"관련 자료 단서: {', '.join(hits[:4])}"
        else:
            decision, reason = "추가 여부 확인", "관련 자료를 찾지 못했습니다. 미집행인지 누락인지 확인하세요."
        child_included[module.section] = child_included.get(module.section, False) or decision in {"자동 포함", "반복 생성"}
        decisions.append(PageDecision(module.key, module.section, module.label, module.mode, decision, len(hits), reason))

    sections = [module for module in MODULES if module.key.startswith("section_")]
    insertion: list[PageDecision] = []
    for module in sections:
        include = child_included.get(module.section, False)
        if module.key == "section_ceremony" and event_type == "29역숏폼왕" and not include:
            decision = "추가 여부 확인"
        else:
            decision = "자동 포함" if include or module.mode == "required" else "추가 여부 확인"
        insertion.append(PageDecision(module.key, module.section, module.label, module.mode, decision, 0, "하위 페이지 구성에 따라 자동 결정됩니다."))

    order = {module.key: index for index, module in enumerate(MODULES)}
    return sorted(decisions + insertion, key=lambda item: order[item.key])
