from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path


def save_project(path: str | Path, source_path: str, event_type: str, plan, evidence=None) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "source_path": source_path,
        "event_type": event_type,
        "report_plan": [asdict(item) for item in plan],
        "evidence": evidence or [],
    }
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
