# /Users/airim/github/hari_fold_django/llm_hub/pred_llm/career.py
import pandas as pd
import numpy as np
import re
from pathlib import Path

DATA_PATH = Path("/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_발령정보.xlsx")
SAVE_PATH = Path("/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_발령정보_result.xlsx")

def normalize_name(x):
    if pd.isna(x): return x
    return re.sub(r"\s+", "", str(x)).strip()

def extract_career_history(df, name, max_steps=15):
    """특정 인물의 최근 발령 이력 (최대 max_steps회)을 문자열로 반환"""
    df = df.copy()
    df["성명"] = df["성명"].apply(normalize_name)

    if name not in df["성명"].values:
        return None

    person = df[df["성명"] == name].iloc[0]

    # 모든 발령단계 추출
    pattern = re.compile(r"(\d+)_발령_부서명")
    steps = sorted([int(x.split("_")[0]) for x in df.columns if pattern.match(x)])

    history = []
    for step in steps:
        dept = person.get(f"{step}_발령_부서명", np.nan)
        job = person.get(f"{step}_발령_직무", np.nan)
        days = person.get(f"{step}_재직일수(현발령~다음발령)", np.nan)

        if pd.isna(dept) and pd.isna(job): 
            continue

        dept = str(dept) if pd.notna(dept) else "-"
        job = str(job) if pd.notna(job) else "-"
        days = int(days) if pd.notna(days) else 0
        history.append(f"{dept}/{job}: {days}일")

    # 최근 max_steps개만 표시
    history = history[-max_steps:] if len(history) > max_steps else history
    return " → ".join(history) if history else "발령 이력이 없습니다."

def build_all_histories():
    df = pd.read_excel(DATA_PATH)
    df["성명"] = df["성명"].apply(normalize_name)
    result = []
    for name in df["성명"].dropna().unique():
        hist = extract_career_history(df, name)
        result.append({"성명": name, "Career_History": hist})
    res_df = pd.DataFrame(result)
    res_df.to_excel(SAVE_PATH, index=False)
    print(f"✅ 커리어 이력 정리 완료 → {SAVE_PATH}")



if __name__ == "__main__":
    build_all_histories()

def format_career_as_table(career_summary: str) -> str:
    """'부서/직무:일수 → 부서/직무:일수' 문자열을 HTML 테이블로 변환 (디자인 개선)"""
    if not career_summary or career_summary == "발령 이력 없음":
        return "<p style='font-size:13px; color:#999;'>발령 이력이 없습니다.</p>"

    records = [r.strip() for r in career_summary.split("→") if r.strip()]
    rows = []

    for rec in records:
        parts = rec.split(":")
        role_part = parts[0].strip() if len(parts) > 0 else ""
        days = parts[1].strip() if len(parts) > 1 else ""
        segs = role_part.split("/")
        dept = segs[0].strip() if len(segs) > 0 else ""
        job = segs[1].strip() if len(segs) > 1 else ""
        rows.append((dept, job, days))

    # ✅ HTML 스타일 향상 (준비도 표와 동일 컨셉)
    table_html = """
    <table style='width:100%; border-collapse:collapse; font-size:12.5px; border:1px solid #ddd;'>
        <thead>
            <tr style='background-color:#f0f3ff; color:#1a3cff; text-align:center;'>
                <th style='padding:8px; border:1px solid #ddd;'>부서/프로젝트</th>
                <th style='padding:8px; border:1px solid #ddd;'>직무</th>
                <th style='padding:8px; border:1px solid #ddd;'>재직일수</th>
            </tr>
        </thead>
        <tbody>
    """

    for i, (dept, job, days) in enumerate(rows):
        bg_color = "#fafbff" if i % 2 == 0 else "#ffffff"  # 🎨 행 줄무늬 효과
        table_html += f"""
            <tr style='text-align:center; background-color:{bg_color};'>
                <td style='padding:6px; border:1px solid #ddd;'>{dept}</td>
                <td style='padding:6px; border:1px solid #ddd;'>{job}</td>
                <td style='padding:6px; border:1px solid #ddd; text-align:right;'>{days}</td>
            </tr>
        """

    table_html += "</tbody></table>"
    return table_html

