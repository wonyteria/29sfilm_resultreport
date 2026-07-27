from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.page_catalog import build_catalog


if __name__ == "__main__":
    files = sorted(Path(".").glob("*.pptx"))
    result = build_catalog(files, "page_catalog.json")
    for report in result["reports"]:
        print(f"{report['file']}: {report['slides']} slides")
        print("  " + ", ".join(f"{key}={value}" for key, value in report["module_counts"].items()))
