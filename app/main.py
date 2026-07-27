from __future__ import annotations

import json
import threading
import os
import tkinter as tk
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .detection import detect_event_type
from .folder_template import create_folder_tree, create_folder_zip
from .readiness import assess_readiness
from .report_plan import build_report_plan
from .scanner import scan_project
from .input_workbook import create_input_workbook
from .content_extract import evidence_as_dict, extract_project_text
from .project_state import save_project
from .quality_gate import inspect_plan
from .template_registry import recommend_templates


class ReportApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("29초영화제 결과보고서 도우미")
        self.geometry("980x700")
        self.minsize(820, 600)
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="사업의 06.결과보고 폴더를 선택하세요.")
        self.current_detection = None
        self.current_plan = None
        self.current_scan = None
        self.current_evidence = []
        self.template_var = tk.StringVar(value="템플릿 추천: 자료 스캔 후 표시")
        self._build_ui()

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=16)
        top.pack(fill="x")
        ttk.Label(top, text="결과보고서 프로젝트", font=("맑은 고딕", 16, "bold")).pack(anchor="w")
        ttk.Label(top, text="NAS의 06.결과보고 폴더를 선택하면 자료를 스캔하고 준비도를 점검합니다.").pack(anchor="w", pady=(2, 12))

        row = ttk.Frame(top)
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.path_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="폴더 선택", command=self.choose_folder).pack(side="left", padx=(8, 0))
        self.scan_button = ttk.Button(row, text="자료 스캔", command=self.start_scan)
        self.scan_button.pack(side="left", padx=(8, 0))

        tools = ttk.Frame(top)
        tools.pack(fill="x", pady=(10, 0))
        ttk.Button(tools, text="표준 폴더 ZIP 저장", command=self.save_zip).pack(side="left")
        ttk.Button(tools, text="표준 폴더 바로 생성", command=self.make_tree).pack(side="left", padx=(8, 0))
        self.input_button = ttk.Button(tools, text="입력 Excel 만들기", command=self.make_input_excel, state="disabled")
        self.input_button.pack(side="left", padx=(8, 0))
        self.project_button = ttk.Button(tools, text="프로젝트 저장", command=self.save_project_file, state="disabled")
        self.project_button.pack(side="left", padx=(8, 0))

        ttk.Separator(self).pack(fill="x")
        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)
        notebook = ttk.Notebook(body)
        notebook.pack(fill="both", expand=True)
        readiness_frame = ttk.Frame(notebook)
        plan_frame = ttk.Frame(notebook)
        notebook.add(readiness_frame, text="자료 준비도")
        notebook.add(plan_frame, text="보고서 구성 제안")

        columns = ("area", "state", "note")
        self.tree = ttk.Treeview(readiness_frame, columns=columns, show="headings", height=14)
        self.tree.heading("area", text="보고서 영역")
        self.tree.heading("state", text="상태")
        self.tree.heading("note", text="안내")
        self.tree.column("area", width=150, anchor="w")
        self.tree.column("state", width=160, anchor="w")
        self.tree.column("note", width=570, anchor="w")
        self.tree.pack(fill="both", expand=True)

        plan_columns = ("section", "label", "decision", "reason")
        self.plan_tree = ttk.Treeview(plan_frame, columns=plan_columns, show="headings", height=14)
        self.plan_tree.heading("section", text="대분류")
        self.plan_tree.heading("label", text="페이지 모듈")
        self.plan_tree.heading("decision", text="구성 제안")
        self.plan_tree.heading("reason", text="판단 근거")
        self.plan_tree.column("section", width=110)
        self.plan_tree.column("label", width=180)
        self.plan_tree.column("decision", width=120)
        self.plan_tree.column("reason", width=480)
        self.plan_tree.pack(fill="both", expand=True)
        ttk.Label(plan_frame, textvariable=self.template_var).pack(anchor="w", pady=(8, 0))
        ttk.Label(plan_frame, text="더블클릭하면 자동 포함 → 추가 여부 확인 → 제외 순서로 변경할 수 있습니다.").pack(anchor="w", pady=(6, 0))
        self.plan_tree.bind("<Double-1>", self._toggle_plan_decision)

        ttk.Label(self, textvariable=self.status_var, padding=(16, 8), relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def choose_folder(self) -> None:
        path = filedialog.askdirectory(title="06.결과보고 폴더 선택")
        if path:
            self.path_var.set(path)

    def start_scan(self) -> None:
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("경로 필요", "프로젝트 폴더 경로를 입력하세요.")
            return
        self.scan_button.config(state="disabled")
        self.status_var.set("자료를 스캔하고 있습니다...")
        threading.Thread(target=self._scan_worker, args=(path,), daemon=True).start()

    def _scan_worker(self, path: str) -> None:
        try:
            scan = scan_project(path)
            detection = detect_event_type(path, scan)
            readiness = assess_readiness(scan)
            plan = build_report_plan(scan, detection.event_type)
            evidence = extract_project_text(path, scan.path_index)
            self.after(0, self._show_result, scan, detection, readiness, plan, evidence)
        except Exception as exc:
            self.after(0, self._show_error, str(exc))

    def _show_result(self, scan, detection, readiness, plan, evidence) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for area in readiness:
            self.tree.insert("", "end", values=(area.area, area.state, area.note))
        for item in self.plan_tree.get_children():
            self.plan_tree.delete(item)
        for page in plan:
            self.plan_tree.insert("", "end", iid=page.key, values=(page.section, page.label, page.decision, page.reason))
        self.current_detection = detection
        self.current_plan = plan
        self.current_scan = scan
        self.current_evidence = evidence
        self.input_button.config(state="normal")
        self.project_button.config(state="normal")
        self.status_var.set(
            f"감지: {detection.event_type} ({detection.confidence}) · 자료 {scan.total_files:,}개 · 제외 {scan.excluded_files:,}개 · {scan.total_bytes / 1024 / 1024:.1f} MB"
        )
        self.scan_button.config(state="normal")
        self._save_scan_report(scan, detection, readiness, plan)

        selected_keys = {item.key for item in plan if item.decision not in {"제외", "미포함"}}
        catalog = Path.cwd() / "page_catalog.json"
        if catalog.exists():
            choices = recommend_templates(catalog, detection.event_type, selected_keys)
            if choices:
                best = choices[0]
                self.template_var.set(f"권장 디자인 기준: {best.filename} · " + " · ".join(best.reasons))

        issues = inspect_plan(plan)
        failed = sum(1 for item in evidence if item.error)
        if issues or failed:
            self.status_var.set(self.status_var.get() + f" · 구성 확인 {len(issues)}건 · 본문 추출 실패 {failed}건")

    def _save_scan_report(self, scan, detection, readiness, plan) -> None:
        output = Path.cwd() / "output"
        output.mkdir(exist_ok=True)
        payload = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "scan": asdict(scan),
            "detection": asdict(detection),
            "readiness": [asdict(x) for x in readiness],
            "report_plan": [asdict(x) for x in plan],
        }
        (output / "최근_자료점검.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _toggle_plan_decision(self, _event=None) -> None:
        selected = self.plan_tree.selection()
        if not selected:
            return
        item = selected[0]
        values = list(self.plan_tree.item(item, "values"))
        cycle = ["자동 포함", "추가 여부 확인", "제외"]
        current = values[2]
        values[2] = cycle[(cycle.index(current) + 1) % len(cycle)] if current in cycle else "자동 포함"
        values[3] = "담당자가 구성을 변경했습니다."
        self.plan_tree.item(item, values=values)

    def _show_error(self, message: str) -> None:
        self.scan_button.config(state="normal")
        self.status_var.set("스캔 실패")
        messagebox.showerror("오류", message)

    def save_zip(self) -> None:
        target = filedialog.asksaveasfilename(
            title="표준 폴더 ZIP 저장",
            defaultextension=".zip",
            initialfile="29초영화제_결과보고_표준폴더.zip",
            filetypes=[("ZIP 파일", "*.zip")],
        )
        if target:
            create_folder_zip(target)
            messagebox.showinfo("완료", f"표준 폴더 ZIP을 저장했습니다.\n{target}")

    def make_tree(self) -> None:
        target = filedialog.askdirectory(title="표준 폴더를 만들 위치 선택")
        if target:
            destination = Path(target) / "06.결과보고"
            create_folder_tree(destination)
            messagebox.showinfo("완료", f"표준 폴더를 만들었습니다.\n{destination}")

    def make_input_excel(self) -> None:
        if not self.current_plan or not self.current_detection:
            messagebox.showwarning("자료 스캔 필요", "먼저 자료 스캔을 실행하세요.")
            return
        initial_dir = str(Path.cwd())
        project_path = self.path_var.get().strip()
        if project_path and Path(project_path).exists():
            local_work = Path.cwd() / "output"
            local_work.mkdir(exist_ok=True)
            initial_dir = str(local_work)
        target = filedialog.asksaveasfilename(
            title="결과보고 입력 Excel 저장",
            initialdir=initial_dir,
            initialfile="결과보고_입력.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel 파일", "*.xlsx")],
        )
        if not target:
            return
        create_input_workbook(target, self.current_detection.event_type, self.current_plan)
        if messagebox.askyesno("완료", f"입력 Excel을 만들었습니다.\n{target}\n\n지금 여시겠습니까?"):
            os.startfile(target)

    def save_project_file(self) -> None:
        if not self.current_plan or not self.current_detection:
            messagebox.showwarning("자료 스캔 필요", "먼저 자료 스캔을 실행하세요.")
            return
        target = filedialog.asksaveasfilename(
            title="결과보고서 프로젝트 저장",
            initialdir=str(Path.cwd() / "output"),
            initialfile="결과보고서_프로젝트.json",
            defaultextension=".json",
            filetypes=[("프로젝트 파일", "*.json")],
        )
        if not target:
            return
        # 화면에서 담당자가 바꾼 포함/제외 결정을 프로젝트에 반영한다.
        by_key = {item.key: item for item in self.current_plan}
        for row_id in self.plan_tree.get_children():
            values = self.plan_tree.item(row_id, "values")
            if row_id in by_key and len(values) >= 3:
                by_key[row_id].decision = values[2]
                if len(values) >= 4:
                    by_key[row_id].reason = values[3]
        save_project(
            target,
            self.path_var.get().strip(),
            self.current_detection.event_type,
            self.current_plan,
            evidence_as_dict(self.current_evidence),
        )
        messagebox.showinfo("저장 완료", f"프로젝트를 저장했습니다.\n{target}")


def main() -> None:
    ReportApp().mainloop()


if __name__ == "__main__":
    main()
