from __future__ import annotations

from dataclasses import dataclass

from .scanner import ScanResult


@dataclass
class Detection:
    event_type: str
    confidence: str
    reasons: list[str]


def detect_event_type(path: str, scan: ScanResult | None = None) -> Detection:
    text = path.lower()
    if scan:
        text += " " + " ".join(scan.sample_paths).lower()
    reasons: list[str] = []
    film_score = 0
    short_score = 0
    if "29역숏폼왕" in text or "숏폼왕" in text:
        short_score += 10
        reasons.append("경로 또는 파일명에서 29역숏폼왕을 확인했습니다.")
    if "29초영화제" in text:
        film_score += 10
        reasons.append("경로 또는 파일명에서 29초영화제를 확인했습니다.")
    if any(word in text for word in ("릴스", "reels", "shorts", "세로형")):
        short_score += 2
        reasons.append("세로형 숏폼 플랫폼 자료가 있습니다.")
    if any(word in text for word in ("시상식", "심사위원", "청소년부", "일반부")):
        film_score += 1

    if film_score == short_score:
        return Detection("확인 필요", "낮음", reasons or ["행사 유형을 판단할 단서가 부족합니다."])
    event_type = "29초영화제" if film_score > short_score else "29역숏폼왕"
    gap = abs(film_score - short_score)
    confidence = "높음" if gap >= 8 else "보통"
    return Detection(event_type, confidence, reasons)
