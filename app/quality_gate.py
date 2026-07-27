from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QualityIssue:
    severity: str
    area: str
    message: str
    action: str


REQUIRED_KEYS = {"cover", "index", "overview", "submission", "award_list", "summary", "closing"}


def inspect_plan(plan) -> list[QualityIssue]:
    issues: list[QualityIssue] = []
    selected = {item.key for item in plan if item.decision not in {"제외", "미포함"}}
    for key in sorted(REQUIRED_KEYS - selected):
        issues.append(QualityIssue("오류", "페이지 구성", f"필수 모듈 '{key}'이 제외되어 있습니다.", "페이지 구성에서 다시 포함하세요."))
    for item in plan:
        if item.decision == "추가 여부 확인":
            issues.append(QualityIssue("확인", item.label, "자료가 없거나 의도적인 생략인지 확정되지 않았습니다.", "포함 또는 제외를 선택하세요."))
    return issues
