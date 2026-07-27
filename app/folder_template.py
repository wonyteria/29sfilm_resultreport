from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path


FOLDERS = [
    "00.입력및안내",
    "01.최종기획안",
    "02.기획및디자인/01.포스터",
    "02.기획및디자인/02.키비주얼",
    "02.기획및디자인/03.홍보영상",
    "02.기획및디자인/04.홈페이지",
    "03.언론홍보/01.보도자료",
    "03.언론홍보/02.온라인기사",
    "03.언론홍보/03.지면기사",
    "03.언론홍보/04.신문광고",
    "04.온라인홍보/01.홈페이지",
    "04.온라인홍보/02.공모전사이트",
    "04.온라인홍보/03.커뮤니티",
    "04.온라인홍보/04.유튜브",
    "04.온라인홍보/05.인스타그램",
    "04.온라인홍보/06.페이스북",
    "04.온라인홍보/07.카카오톡",
    "04.온라인홍보/08.SMS",
    "04.온라인홍보/09.뉴스레터",
    "04.온라인홍보/10.디지털광고/00.통합요약",
    "04.온라인홍보/10.디지털광고/01.구글",
    "04.온라인홍보/10.디지털광고/02.카카오",
    "04.온라인홍보/10.디지털광고/03.메타",
    "04.온라인홍보/10.디지털광고/04.네이버",
    "04.온라인홍보/11.오픈채팅방",
    "04.온라인홍보/12.기타SNS",
    "05.오프라인홍보/01.포스터배포/00.대표사진",
    "05.오프라인홍보/01.포스터배포/서울",
    "05.오프라인홍보/01.포스터배포/경기",
    "05.오프라인홍보/01.포스터배포/기타지역",
    "05.오프라인홍보/02.옥외광고",
    "05.오프라인홍보/03.교통광고",
    "05.오프라인홍보/04.현장홍보",
    "05.오프라인홍보/05.기타",
    "06.출품현황/01.최종출품목록",
    "06.출품현황/02.일자별현황",
    "06.출품현황/03.부문별집계",
    "06.출품현황/04.플랫폼별집계",
    "06.출품현황/05.출품현황캡처",
    "07.심사/01.최종심사기획안",
    "07.심사/02.심사위원",
    "07.심사/03.심사기준",
    "07.심사/04.예심결과",
    "07.심사/05.본심결과",
    "07.심사/06.현장사진",
    "08.수상작/01.수상작목록",
    "08.수상작/02.대표이미지",
    "08.수상작/03.시놉시스",
    "08.수상작/04.영상URL",
    "09.시상식및결과발표/00.최종시상식기획안",
    "09.시상식및결과발표/01.행사개요",
    "09.시상식및결과발표/02.큐시트",
    "09.시상식및결과발표/03.참석자",
    "09.시상식및결과발표/04.제작물",
    "09.시상식및결과발표/05.현장사진",
    "09.시상식및결과발표/06.온라인중계",
    "09.시상식및결과발표/07.결과발표",
    "10.참석자및후기/01.참석자",
    "10.참석자및후기/02.현장사진",
    "10.참석자및후기/03.사진캡션",
    "10.참석자및후기/04.참가자후기",
    "10.참석자및후기/05.수상자후기",
    "10.참석자및후기/06.SNS후기",
    "10.참석자및후기/07.주최사피드백",
    "11.성과및총평/01.통합성과",
    "11.성과및총평/02.총평메모",
    "12.기타자료",
    "90.작업중/01.점검표",
    "90.작업중/02.PPT초안",
    "99.최종/생성기록",
]

README = """29초영화제·29역숏폼왕 결과보고 자료 폴더

1. 해당하는 폴더에만 자료를 넣어도 됩니다.
2. 진행하지 않은 활동은 프로그램에서 '해당 없음'으로 확인합니다.
3. 숫자·날짜·인명은 프로그램이 추출한 뒤 담당자가 최종 확인합니다.
4. 90.작업중과 99.최종에는 원본 자료를 넣지 마세요.
5. 기존 결과보고서와 제작 중 PPTX는 프로그램 스캔에서 제외됩니다.

자세한 폴더별 자료 목록은 프로그램과 함께 제공된
docs/MATERIAL_CHECKLIST.md를 확인하세요.
"""


def _csv_bytes(headers: list[str], example: list[str] | None = None) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(headers)
    if example:
        writer.writerow(example)
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")


def create_folder_zip(destination: str | Path) -> Path:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zf:
        directories: set[str] = set()
        for folder in FOLDERS:
            parts = folder.replace("\\", "/").strip("/").split("/")
            for index in range(1, len(parts) + 1):
                directories.add("/".join(parts[:index]) + "/")
        for folder in sorted(directories):
            zf.writestr(folder, "")
        zf.writestr("00.입력및안내/README.txt", README.encode("utf-8-sig"))
        zf.writestr(
            "00.입력및안내/기본정보.csv",
            _csv_bytes(["항목", "값", "상태", "근거파일", "비고"], ["사업명", "", "미입력", "", ""]),
        )
        zf.writestr(
            "06.출품현황/출품현황_입력.csv",
            _csv_bytes(["기준일", "구분", "출품수", "상태", "근거파일"]),
        )
        zf.writestr(
            "08.수상작/수상작_입력.csv",
            _csv_bytes(["순서", "상격", "부문", "수상자", "작품명", "상금", "URL", "시놉시스", "대표이미지"]),
        )
        zf.writestr(
            "00.입력및안내/프로젝트_초기설정.json",
            json.dumps({"schema_version": 1, "event_type": "", "project_name": "", "status": "자료수집중"}, ensure_ascii=False, indent=2),
        )
    return destination


def create_folder_tree(destination: str | Path) -> Path:
    destination = Path(destination)
    for folder in FOLDERS:
        (destination / folder).mkdir(parents=True, exist_ok=True)
    (destination / "00.입력및안내" / "README.txt").write_text(README, encoding="utf-8-sig")
    return destination
