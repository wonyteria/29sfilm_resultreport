from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


EXCLUDED_DIRS = {"90.작업중", "99.최종", "최종", "00.결과보고서"}
TEMP_SUFFIXES = {".tmp", ".bak"}
SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff", ".pdf", ".pptx", ".xlsx", ".csv", ".docx", ".hwpx", ".hwp", ".mp4", ".mov"}


@dataclass
class ScanResult:
    root: str
    total_files: int = 0
    total_bytes: int = 0
    excluded_files: int = 0
    unreadable_files: list[str] = field(default_factory=list)
    unsupported_files: list[str] = field(default_factory=list)
    empty_files: list[str] = field(default_factory=list)
    by_top_folder: dict[str, int] = field(default_factory=dict)
    by_extension: dict[str, int] = field(default_factory=dict)
    sample_paths: list[str] = field(default_factory=list)
    path_index: list[str] = field(default_factory=list)


def _excluded(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIRS for part in relative_parts[:-1]):
        return True
    name = path.name.lower()
    return name.startswith("~$") or "결과보고서" in name or path.suffix.lower() in TEMP_SUFFIXES


def scan_project(root_value: str) -> ScanResult:
    root = Path(root_value)
    if not root.exists() or not root.is_dir():
        raise ValueError("입력한 프로젝트 폴더를 찾을 수 없습니다.")

    result = ScanResult(root=str(root))
    folder_counts: Counter[str] = Counter()
    ext_counts: Counter[str] = Counter()

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _excluded(path, root):
            result.excluded_files += 1
            continue
        try:
            size = path.stat().st_size
        except OSError:
            result.unreadable_files.append(str(path))
            continue
        result.total_files += 1
        result.total_bytes += size
        if size == 0:
            result.empty_files.append(str(path))
        ext = path.suffix.lower() or "(확장자 없음)"
        ext_counts[ext] += 1
        relative = path.relative_to(root)
        top = relative.parts[0] if relative.parts else "(루트)"
        folder_counts[top] += 1
        if ext not in SUPPORTED:
            result.unsupported_files.append(str(path))
        if len(result.sample_paths) < 100:
            result.sample_paths.append(str(relative))
        if len(result.path_index) < 5000:
            result.path_index.append(str(relative))

    result.by_top_folder = dict(folder_counts.most_common())
    result.by_extension = dict(ext_counts.most_common())
    return result
