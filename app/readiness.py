from __future__ import annotations

from dataclasses import dataclass

from .scanner import ScanResult


@dataclass
class AreaStatus:
    area: str
    state: str
    note: str


ALIASES = {
    "사업개요": ("01.최종기획안", "최종기획안", "기획안"),
    "사업홍보": ("언론홍보", "온라인홍보", "오프라인홍보", "보도자료", "올콘", "광고", "포스터배포", "gbus", "에브리타임"),
    "출품현황": ("06.출품현황", "출품현황", "출품"),
    "심사": ("07.심사", "심사기획안", "심사위원"),
    "수상작": ("08.수상작", "수상작", "수상자"),
    "시상식": ("09.시상식", "시상식", "큐시트"),
    "참석자·후기": ("10.참석자", "참석자", "후기", "현장사진"),
    "총평": ("11.성과", "총평", "통합성과"),
}


def assess_readiness(scan: ScanResult) -> list[AreaStatus]:
    haystack = " ".join(scan.by_top_folder).lower() + " " + " ".join(scan.sample_paths).lower()
    results: list[AreaStatus] = []
    for area, aliases in ALIASES.items():
        found = [alias for alias in aliases if alias.lower() in haystack]
        if found:
            state = "자료 발견"
            note = f"관련 단서: {', '.join(found[:3])}"
        elif area in {"수상작", "참석자·후기"}:
            state = "직접 입력 필요"
            note = "담당자 확정 정보가 필요합니다."
        elif area == "총평":
            state = "초안 대기"
            note = "핵심 성과 확정 후 AI 초안을 생성합니다."
        else:
            state = "자료 없음/확인 필요"
            note = "미집행인지 자료 누락인지 확인해야 합니다."
        results.append(AreaStatus(area, state, note))
    return results
