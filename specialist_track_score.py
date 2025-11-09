import pandas as pd
import re
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from io import BytesIO
import platform
from pathlib import Path

# -------------------------------------------------
# ✅ macOS 한글 폰트 세팅 (Streamlit 호환)
# -------------------------------------------------
def get_korean_font():
    """macOS에서 사용 가능한 한글 폰트 객체 반환"""
    if platform.system() == "Darwin":
        font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
        if Path(font_path).exists():
            font_prop = FontProperties(fname=font_path)
            return font_prop
    # fallback
    return FontProperties(fname=fm.findfont(fm.FontProperties(family="Arial Unicode MS")))

# -------------------------------------------------
# Helper
# -------------------------------------------------
def _norm(s: str) -> str:
    if s is None:
        return ""
    return re.sub(r"\s+", "", str(s)).lower().strip()


def find_col(cols, target_startswith: str):
    norm_target = _norm(target_startswith)
    for c in cols:
        if _norm(c).startswith(norm_target):
            return c
    return None


def find_rank_cols(cols, prefix: str):
    found = []
    for i in range(1, 6):
        want = f"{prefix}{i}순위"
        col = find_col(cols, want)
        if col:
            found.append((i, col))
    return [c for _, c in sorted(found, key=lambda x: x[0])]


def build_transition_network(df, rank_cols):
    pairs = []
    for _, row in df.iterrows():
        jobs = [str(row[c]).strip() for c in rank_cols if pd.notna(row[c]) and str(row[c]).strip()]
        for a, b in zip(jobs[:-1], jobs[1:]):
            pairs.append((a, b))
    if not pairs:
        return pd.DataFrame(columns=["from", "to", "weight"])
    edge_df = pd.DataFrame(pairs, columns=["from", "to"])
    edge_weights = edge_df.groupby(["from", "to"]).size().reset_index(name="weight")
    return edge_weights


# -------------------------------------------------
# 🎨 Streamlit용 그래프 빌드
# -------------------------------------------------
def build_specialist_graph_for_streamlit(xlsx_path: str):
    df = pd.read_excel(xlsx_path).fillna("")
    cols = df.columns.tolist()
    font_prop = get_korean_font()

    track_col = find_col(cols, "희망하시는 최종 커리어 목표를 선택해주세요")
    if not track_col:
        raise KeyError("⚠️ '희망하시는 최종 커리어 목표를 선택해주세요.' 컬럼을 찾을 수 없습니다.")

    five_prefix = "커리어 목표 달성에 필요한 5년 후 직무 "
    ten_prefix = "커리어 목표 달성에 필요한 10년 후 직무 "

    five_cols = find_rank_cols(cols, five_prefix)
    ten_cols = find_rank_cols(cols, ten_prefix)
    all_cols = list(set(five_cols + ten_cols))
    tracks = sorted(df[track_col].astype(str).str.strip().unique())

    all_graphs = {}

    for tr in tracks:
        sub = df[df[track_col].astype(str).str.strip() == tr]
        if sub.empty:
            continue

        edge_df = build_transition_network(sub, all_cols)
        if edge_df.empty:
            continue

        # 네트워크
        G = nx.DiGraph()
        for _, r in edge_df.iterrows():
            G.add_edge(r["from"], r["to"], weight=r["weight"])

        # 중심성 계산
        degree_centrality = nx.degree_centrality(G)
        betweenness = nx.betweenness_centrality(G, weight="weight")

        pos = nx.spring_layout(G, k=0.6, seed=42)
        node_sizes = [800 + degree_centrality[n] * 4500 for n in G.nodes()]
        node_colors = [betweenness[n] for n in G.nodes()]
        edge_weights = [max(0.8, G[u][v]["weight"]) for u, v in G.edges()]

        # 🎨 그래프
        fig, ax = plt.subplots(figsize=(8, 6))
        nx.draw_networkx_edges(
            G, pos, width=edge_weights, alpha=0.4, edge_color="#003C71",
            arrows=True, arrowsize=14, connectionstyle="arc3,rad=0.1"
        )
        nodes = nx.draw_networkx_nodes(
            G, pos, node_size=node_sizes, node_color=node_colors,
            cmap=plt.cm.coolwarm, alpha=0.9, linewidths=0.7, edgecolors="white"
        )

        # ✅ 라벨에 폰트 강제 적용
        nx.draw_networkx_labels(
            G, pos, 
            font_size=9, 
            font_color="#111", 
            font_family='Apple SD Gothic Neo',
            # fontproperties=font_prop
        )

        ax.set_title(f"{tr} 직무 SNA 그래프", fontsize=14, fontweight="bold", color="#003C71", pad=15, fontproperties=font_prop)
        cbar = plt.colorbar(nodes, ax=ax)
        cbar.set_label("매개 중심성 (Betweenness Centrality)", fontsize=10, color="#003C71", fontproperties=font_prop)
        ax.axis("off")
        plt.tight_layout()

        # 결과 구조
        centrality_df = pd.DataFrame({
            "직무": list(G.nodes()),
            "Degree": [degree_centrality[n] for n in G.nodes()],
            "Betweenness": [betweenness[n] for n in G.nodes()]
        }).sort_values("Degree", ascending=False)

        all_graphs[tr] = {"figure": fig, "중심성": centrality_df}

    return all_graphs
