# /Users/airim/github/hari_fold_django/llm_hub/pred_llm/gen_speacial_score.py
import pandas as pd
import numpy as np
import re

# ===== 공통 =====
GENERAL_COLS = [
    "Tanage_강점_외교","Tanage_강점_조정","Tanage_강점_평가",
    "Tanage_재능_사교_행동","Tanage_재능_친밀_행동","Tanage_재능_유연_행동",
    "Tanage_재능_창의_행동","Tanage_커리어_유연함_욕구",
    "CJPI외현행동_팀워크","CJPI외현행동_리더십"
]
SPECIAL_COLS = [
    "Tanage_강점_완성","Tanage_강점_탐구","Tanage_재능_달성_행동",
    "Tanage_재능_완벽_행동","Tanage_재능_몰입_행동","Tanage_재능_논리_행동",
    "Tanage_재능_전략_행동","Tanage_커리어_분석적_욕구"
]

def normalize_col(c: str) -> str:
    c = (c or "").replace("\ufeff", "")
    c = re.sub(r"\s*_\s*", "_", c)
    c = re.sub(r"\s+", " ", c).strip()
    return c

def safe_mean(row, cols, min_non_na=2):
    vals = row[cols].dropna() if cols else []
    return vals.mean() if len(vals) >= min_non_na else np.nan

def compute_general_special_scores(df: pd.DataFrame, name: str) -> dict:
    """Streamlit에서 직접 호출용: 특정 인물의 G/S 점수 계산"""
    df = df.copy()
    df.columns = [normalize_col(c) for c in df.columns]

    if name not in df["성명"].values:
        return {"G_score": np.nan, "S_score": np.nan, "valid": False}

    person_row = df[df["성명"] == name].iloc[0]

    GEN_AVAIL = [c for c in GENERAL_COLS if c in df.columns]
    SPE_AVAIL = [c for c in SPECIAL_COLS if c in df.columns]

    # 개인 원시 평균
    raw_G = safe_mean(person_row, GEN_AVAIL)
    raw_S = safe_mean(person_row, SPE_AVAIL)

    # 전체 데이터 기준 정규화
    G_raw_all = df[GEN_AVAIL].mean(axis=1, skipna=True)
    S_raw_all = df[SPE_AVAIL].mean(axis=1, skipna=True)

    def minmax_val(value, series):
        if pd.isna(value) or series.isna().all():
            return np.nan
        rng = series.max() - series.min()
        if rng == 0:
            return 0.5
        return (value - series.min()) / rng

    G_norm = minmax_val(raw_G, G_raw_all)
    S_norm = minmax_val(raw_S, S_raw_all)

    if pd.isna(G_norm) and pd.isna(S_norm):
        return {"G_score": np.nan, "S_score": np.nan, "valid": False}

    # 합이 1이 되도록 보정
    total = (G_norm or 0) + (S_norm or 0)
    if total == 0:
        G_score, S_score = 0.5, 0.5
    else:
        G_score = G_norm / total if pd.notna(G_norm) else 0.0
        S_score = 1 - G_score

    return {
        "G_score": round(float(G_score), 3),
        "S_score": round(float(S_score), 3),
        "valid": True
    }
