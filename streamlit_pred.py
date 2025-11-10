# 파일명: /Users/airim/github/hari_fold_django/llm_hub/pred_llm/streamlit_pred.py

import streamlit as st
import pandas as pd
import time
# from rapidfuzz import process, fuzz
import os
import base64
import os, sys, io, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit.components.v1 as components

# ------------------------------------------------
# 페이지 설정
# ------------------------------------------------
st.set_page_config(page_title="CDP 가이드 생성기", layout="wide")

# ------------------------------------------------
# 데이터 경로 (기존 경로 유지)
# ------------------------------------------------
BASE_DIR = os.path.dirname(__file__)

# EMPLOYEE_PATH = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only인사.xlsx"
# SCORE_PATH    = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_specialist_generalist_score_result.xlsx"
# CAREER_PATH   = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_발령정보_result.xlsx"
# LOGO_PATH     = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/assets/cj_company.png"
# 
# EMP_PATH = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_발령정보.xlsx"
# MAP_PATH = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/핵심직무_유사직무_매핑.xlsx"

# 상대경로로 각 파일 지정
EMPLOYEE_PATH = os.path.join(BASE_DIR, "data", "only인사.xlsx")
SCORE_PATH    = os.path.join(BASE_DIR, "data", "only_specialist_generalist_score_result.xlsx")
CAREER_PATH   = os.path.join(BASE_DIR, "data", "only_발령정보_result.xlsx")
LOGO_PATH     = os.path.join(BASE_DIR, "assets", "cj_company.png")

EMP_PATH = os.path.join(BASE_DIR, "data", "only_발령정보.xlsx")
MAP_PATH = os.path.join(BASE_DIR, "data", "핵심직무_유사직무_매핑.xlsx")

# ------------------------------------------------
# 유틸
# ------------------------------------------------
def image_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

logo_b64 = image_to_base64(LOGO_PATH)

# ------------------------------------------------
# 데이터 로드 (데모는 하드코딩 출력이라 실패해도 진행)
# ------------------------------------------------
merged_df = None
try:
    # 기존 코드와의 호환을 위해 최소한의 로드만 수행
    employee_df = pd.read_excel(EMPLOYEE_PATH)
    if "성명" in employee_df.columns:
        employee_df["성명"] = employee_df["성명"].astype(str).str.replace(r"\s+", "", regex=True).str.strip()
        merged_df = employee_df
except Exception:
    pass

# ------------------------------------------------
# CSS
# ------------------------------------------------
st.markdown(f"""
    <style>
    .header-container {{
        display: flex; flex-direction: column; align-items: center; text-align: center;
        margin-top: 20px; margin-bottom: 25px;
    }}
    .header-title-text {{
        font-size: 26px; font-weight: 600; font-family: "Segoe UI","Helvetica Neue",sans-serif;
        background: linear-gradient(90deg, #0059ff 0%, #00c6ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .card-list {{ display: flex; flex-direction: column; gap: 12px; margin-top: 15px; margin-bottom: 30px; }}
    .card-logo {{ width: 36px; height: 36px; border-radius: 50%; object-fit: cover; }}
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# Header
# ------------------------------------------------


# ------------------------------------------------
# HARI Career Report 안내 문구
# ------------------------------------------------
MAIN_IMG_PATH = os.path.join(BASE_DIR, "assets", "main_2.png")



def load_image_base64(path):
    """이미지를 base64로 읽어 HTML로 렌더링"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 이미지 로드
main_img_b64 = load_image_base64(MAIN_IMG_PATH)

# Streamlit UI에 렌더링
st.markdown(
    f"""
    <div style="text-align:center; margin-bottom:30px;">
        <img src="data:image/png;base64,{main_img_b64}" 
             alt="HARI Main Banner" style="max-width:40%; border-radius:10px;">
    </div>
    """, unsafe_allow_html=True
)


# ------------------------------------------------
# 상태
# ------------------------------------------------
if "selected_person" not in st.session_state:
    st.session_state.selected_person = None

# ------------------------------------------------
# 검색 입력
# ------------------------------------------------
# ser_col1, ser_col2, ser_col3 = st.columns([1, 1, 1])
# with ser_col2:
    # search_name = st.text_input(
        # "",
        # placeholder="안녕하세요. 예측/분석모델 Module 에게 질문해주세요.",
        # label_visibility="collapsed"
    # )


st.markdown("""
<div style="color:#6e6e6e; text-align:center;"">
[HARI 추천 프롬프트]<br>
정열창님의 태니지먼트 결과와 대한통운 건설부문에서의 경험으로 봤을 때 Generalist, Specialist 성향이 어떻게 되는지와 회사 내에서 어떤 Track으로 성장하면 좋을지 추천해줘.
</div>
""", unsafe_allow_html=True)
st.divider()
search_name = st.text_input(
    "",
    placeholder="안녕하세요. 예측/분석모델 Module 에게 질문해주세요.",
    label_visibility="collapsed"
)




# ------------------------------------------------
# 데모용 하드코딩 컨텐츠 (누구를 선택해도 동일)
# ------------------------------------------------
REPORT_PERSON = "정열창001"

CAREER_PRE_BLOCK = """건축시공 22개월 / 건축공무 21개월 / 건축PM 15개월 / 건축PE 1개월 / CS 2개월 / 현장소장 15개월"""

GENERAL_SCORE_PCT = 10
SPECIAL_SCORE_PCT = 90

# General 카드 안에 들어갈 좌측 본문 HTML (요청 텍스트 그대로)
GENERAL_CARD_HTML = f"""
<div style="
    border: 1px solid #ddd; border-radius: 8px; padding: 15px 20px;
    background-color: #fcfcfc; box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    font-family: 'Segoe UI', sans-serif; color:#222;">
    <h3 style="color:#1a3cff; margin-bottom:10px; text-align:center;">
        General Track Report<br>
        <span style="color:#777; font-size:18px; text-align:center; margin-bottom:6px;">
            추천지수: {GENERAL_SCORE_PCT}%
        </span>
    </h3>

    <div style="text-align:center; margin:12px 0 8px 0; font-weight:700;">{REPORT_PERSON}님의 커리어 가이드 레포트</div>
    <hr style="margin:12px 0; border:none; border-top:1px solid #e0e0e0;">

    <div style="font-weight:700; margin-top:8px; margin-bottom:6px;">{REPORT_PERSON}님의 직무 경험 (CJ 內 경력)</div>
    <pre style="
        background:#f7f8fb; border:1px solid #e0e5f2; border-radius:6px; padding:12px; 
        font-size:13px; line-height:1.5; overflow-x:auto; white-space:pre;">
{CAREER_PRE_BLOCK}
    </pre>

    <hr style="margin:16px 0; border:none; border-top:1px solid #e0e0e0;">

    <div style="margin:10px 0;">
        Tangement 재능 기반으로 정열창001님의 커리어 추천은<br>
        <b>Generalist {GENERAL_SCORE_PCT}%, Specialist {SPECIAL_SCORE_PCT}%</b>입니다
    </div>

    <div style="margin:12px 0;">
        Tangement 재능 기반으로 {REPORT_PERSON}님의 최종 Track은<br>
        <b>공사담당 Track 추천드립니다.</b>
    </div>

    <hr style="margin:16px 0; border:none; border-top:1px solid #e0e0e0;">

    <div style="margin-bottom:8px; font-weight:700;">▶ 공사담당 필요 역량</div>
    <table style="width:100%; border-collapse:collapse; font-size:12.5px;">
        <thead>
            <tr>
                <th style="border:1px solid #ddd; padding:6px;">프로젝트 관리 역량</th>
                <th style="border:1px solid #ddd; padding:6px;">문제 해결 역량</th>
                <th style="border:1px solid #ddd; padding:6px;">의사소통 및 협상 역량</th>
                <th style="border:1px solid #ddd; padding:6px;">재무 및 비용 관리 역량</th>
                <th style="border:1px solid #ddd; padding:6px;">다양한 프로젝트 수행 경험</th>
                <th style="border:1px solid #ddd; padding:6px;">리더십</th>
            </tr>
        </thead>
    </table>

    <div style="margin-top:14px; font-size:13px; line-height:1.6; color:#333;">
        프로젝트를 수주하면 제일 먼저 해야 하는 것은 전체 공정표를 짜는 일입니다.
        그 안에는 말 그대로 처음부터 끝까지 모든 단계가 다 포함됩니다. 이 일은 단순히 일정을 나열하는 것이 아니라,
        목적을 완성하기 위해 어떤 순서로, 어떤 자원을 활용하고, 어떤 리스크를 감안해야 하는지를 세밀하게 설계해야 합니다.
        <br><br>
        공정을 만들 때는 각 단계를 세분화하여 수행 방법까지 구체적으로 검토합니다.
        예를 들어, 주간·월간 공정표를 각각 작성하여 실제 현장에서 수행 가능한 수준으로 맞춥니다.
        공사 진행 중에는 계획 대비 실적을 지속적으로 비교하고, 차이가 발생하면 그 원인을 분석합니다.
        자재 지연, 인력 배치, 기상 조건, 대관 문제 등 구체적인 요인을 검토합니다.
        <br><br>
        결국 이 일은 단순히 ‘계획을 세우는 것’이 아니라
        ‘계획이 살아 움직이도록 관리하는 일’에 가깝습니다.
        그래야 공정 단축 전략이 현실에서 작동하고, 수주 시점에 약속한 일정 내 완공이 가능합니다.
    </div>
</div>
"""

# Specialist 카드: 점수 고정, 그래프는 공란 placeholder
SPECIAL_CARD_HTML = f"""
<div style="
    border: 1px solid #ddd; border-radius: 8px; padding: 15px 20px;
    background-color: #fcfcfc; box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    font-family: 'Segoe UI', sans-serif; color:#222;">
    <h3 style="color:#FF8C42; margin-bottom:10px; text-align:center;">
        Specialist Track Report<br>
        <span style="color:#777; font-size:18px;">
            추천지수: {SPECIAL_SCORE_PCT}%
        </span>
    </h3>

    <div style="text-align:center; margin:12px 0 8px 0; font-weight:700;">과거 경험 디브리핑</div>
    <pre style="
        background:#f7f8fb; border:1px solid #e0e5f2; border-radius:6px; padding:12px; 
        font-size:13px; line-height:1.5; overflow-x:auto; white-space:pre;">
{CAREER_PRE_BLOCK}
    </pre>

    <hr style="margin:16px 0; border:none; border-top:1px solid #e0e0e0;">

    <div style="text-align:center; font-weight:700; color:#FF8C42;">CDP 성공 가이드 SNA</div>
    <div style="
        margin-top:12px; width:100%; height:420px; border:1px dashed #ffc9a6;
        display:flex; align-items:center; justify-content:center; color:#c77532; background:#fffaf5;">
        그래프 이미지를 여기에 추가할 수 있습니다. (placeholder)
    </div>
</div>
"""

# ------------------------------------------------
# 리포트 출력 (선택 시)
# ------------------------------------------------
# ... (import 및 초기 설정은 기존 그대로 유지)

# ---- 리포트 출력 ----
# 선택된 인물이 있을 때
if search_name.strip():
    # 프로그래스 바 시각 효과
    with st.spinner("sLLM이 현재 CDP 리포트를 생성하고 있습니다. 잠시만 기다려 주세요."):
        progress_bar = st.progress(0)
        for step in range(1, 101):
            progress_bar.progress(step)
            time.sleep(0.1)  # 0.01초 * 100 → 약 1초 소요
        time.sleep(3.0)  # 추가 딜레이
    # 모든 결과는 고정된 '정열창001' 기준으로 처리
    person_name = "정열창001"
    
    st.markdown(f"""
    ## {person_name}님의 커리어 가이드 레포트

    ---

    ### {person_name}님의 직무 경험 (CJ 內 경력)

    <table style="width:100%; border-collapse:collapse; text-align:center; font-size:14px;">
        <tr style="background-color:#f3f6ff; font-weight:600;">
            <td style="padding:6px;">프로젝트 매니저</td>
            <td style="padding:6px;">구매관리</td>
        </tr>
        <tr>
            <td style="padding:6px;">59개월</td>
            <td style="padding:6px;">17개월</td>
        </tr>
    </table>

    <br>

    <table style="width:100%; border-collapse:collapse; text-align:center; font-size:14px;">
        <tr style="background-color:#f9fafc; font-weight:600;">
            <td style="padding:6px;">건축시공</td>
            <td style="padding:6px;">건축공무</td>
            <td style="padding:6px;">건축PM</td>
            <td style="padding:6px;">건축PE</td>
            <td style="padding:6px;">CS</td>
            <td style="padding:6px;">현장소장</td>
        </tr>
        <tr>
            <td style="padding:6px;">22개월</td>
            <td style="padding:6px;">21개월</td>
            <td style="padding:6px;">15개월</td>
            <td style="padding:6px;">1개월</td>
            <td style="padding:6px;">2개월</td>
            <td style="padding:6px;">15개월</td>
        </tr>
    </table>
    
    ---
    #### ▶ Tanagement 재능 기반으로 정열창님의 커리어 추천은 <span style="color:#1a3cff; font-weight:bold;">Generalist 10%</span>, <span style="color:#E42F44; font-weight:bold;">Specialist 90%</span>입니다

    #### ▶ Tanagement 재능 기반으로 정열창님의 최종 Track은 <span style="color:#EC8922; font-weight:bold;">공사담당 Track </span>입니다.
    
    ---

    ### ▶ 공사담당 필요 역량
    
    | 프로젝트 관리 역량 | 문제 해결 역량 | 의사소통 및 협상 역량 | 재무 및 비용 관리 역량 | 다양한 프로젝트 수행 경험 | 리더십 |
    |----------|--------|------------|-------------|--------------|---|
    
    프로젝트를 수주하면 제일 먼저 해야 하는 것은 전체 공정표를 짜는 일입니다. 그 안에는 말 그대로 처음부터 끝까지 모든 단계가 다 포함됩니다.  
    이 일은 단순히 일정을 나열하는 것이 아니라, 목적을 완성하기 위해 어떤 순서로, 어떤 자원을 활용하고,
    어떤 리스크를 감안해야 하는지를 세밀하게 설계해야 합니다.
    
    공정을 만들 때는 각 단계를 세분화하여 수행 방법까지 구체적으로 검토합니다. 예를 들어, 주간·월간 공정표를 각각 작성하여 실제 현장에서 
    수행 가능한 수준으로 맞춥니다.  
    공사 진행 중에는 계획 대비 실적을 지속적으로 비교하고, 차이가 발생하면 그 원인을 분석합니다. 자재 지연, 인력 배치, 기상 조건,
    대관 문제 등 구체적인 요인을 검토합니다.
    
    결국 이 일은 단순히 ‘계획을 세우는 것’이 아니라 ‘계획이 살아 움직이도록 관리하는 일’에 가깝습니다.  
    그래야 공정 단축 전략이 현실에서 작동하고, 수주 시점에 약속한 일정 내 완공이 가능합니다.
    
    ---
    """, unsafe_allow_html=True)

    # ---- 아래부터 Generalist / Specialist 두 카드 영역 ----
    st.markdown(
    """
    <h3 style='text-align: center;'>
        Generalist / Specialist Career Development Plan
    </h3>
    """,
    unsafe_allow_html=True
)
    col1, col2 = st.columns(2)
    
    TRACK_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "track_image.png")

    base64_image_string = image_to_base64(TRACK_IMAGE_PATH)
    # === Generalist Track ===
    with col1:
        general_html = f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px 20px;
            background-color: #fcfcfc;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            font-family: 'Segoe UI', sans-serif;
        ">
            <h3 style="color:#1a3cff;text-align:center;">Generalist Track Report</h3>
            <p style="text-align:center;font-size:18px;margin-top:-8px;"><b>추천지수: 10%</b></p>
            
            <hr style="margin:10px 0;border-top:1px solid #eee;">
    
            <b>Generalist 추천 Logic</b><br>
            Generalist Track은 직무 간 경계를 넘나들며 균형 있는 역량을 축적한 융합형 인재를 육성하기 위해, 
            다양한 직무 경험과 다차원적 역할 수행 가능성을 중심으로 추천 직무를 도출합니다.
            

            <br><br><b>📌 단기 추천: 안전경영</b><br><br>
            안전경영 직무에서는 현장의 위험 요소를 사전에 식별하고 통제해야 하므로 품질·안전·환경(QSE) 관리 능력을 실질적으로 기를 수 있습니다. 
            건설 현장은 중장비 운용, 고소 작업, 협력업체 동시 투입 등 다양한 위험요인을 내포하고 있으며, 이를 예방하기 위해 안전경영 담당자는 
            공정별 위험성 평가를 실시하고 예방조치를 체계적으로 수립합니다. 
            
            또한 협의체 구성과 공기 조절 작업을 통해 일정에 왜곡이 없기 때문에, 품질 기준과 환경 관리 기준을 함께 통합적으로 검토합니다. 
            비산먼지, 폐기물, 소음 등 외부 환경 리스크에 대해서도 지속적으로 모니터링하며, 관련 법규와 정부 지침을 준수해 행정 리스크를 차단합니다. 
            이러한 활동을 통해 안전경영 역량을 갖춘 담당자는 단순한 현장 관리자가 아니라, 품질·안전·환경 분야를 아우르는 통합형 역량을 갖추게 됩니다. 
            결국 안전 직무는 사고를 미연에 방지하는 일을 넘어, 기업의 QSE 수준을 선제적으로 향상시키는 전략적 역할을 수행하며 현장에서 
            역량을 가장 실질적으로 발전시킬 수 있는 영역입니다.
          
       
            <br><br><b>📌 중기 추천: 인력확보 유지 및 육성</b><br><br>
            인력 확보·유지 및 육성(인사) 직무에서는 구성원과 조직 간의 관계를 다루기 때문에 의사소통 능력을 가장 인접한 중점직으로 기를 수 있습니다. 
            인사 담당자는 채용, 평가, 보상, 교육 등 인력 관련 전 과정에서 구성원의 다양한 입장과 감정을 조율해야 하며, 
            이를 위해 신뢰 기반의 커뮤니케이션이 필수적입니다. 채용 단계에서는 지원자가 직무와 조직에 적합한지 비전과 직무를 명확히 판단해야 하고, 
            내부적으로는 경영진과 관련 부서 간 업무 조율과 역할 방향을 중재해야 합니다. 또한 교육과 평가 과정에서는 피드백을 주고받으며 
            구성원의 성장 지원을 총괄하는 역할을 맡게 되므로, 객관과 조화를 의사소통으로 기술이 요구됩니다. 
            
            이런 경험을 통해 인사 담당자는 단순한 행정 전문가가 아니라, 조직 내 신뢰를 형성하고 구성원의 몰입과 성장을 지원하는 관계 조율자로서의 
            커뮤니케이션 역량을 발전시킬 수 있습니다.
            
            
    
            <br><br><b>📌 장기 추천: 자원관리</b><br><br>
            자원관리 직무에서는 프로젝트의 공정 계획을 실제 실행 가능한 형태로 전환하고 유지해야 하기 때문에 
            전략적 계획 및 일정 관리 능력을 핵심적으로 기를 수 있습니다. 건설 현장은 자재, 장비, 인력 등 다양한 자원이 
            유기적으로 연결되어 운영되는 구조이므로, 일정 계획을 세울 때 단순한 순서 나열이 아니라 자원 투입의 타이밍과 리스크를 
            고려한 통합 운영이 필요합니다. 자원관리 담당자는 계획 대비 실적을 점검하며 계획 대비 실적 차이를 분석합니다. 
            
            자재 지연이나 인력 수급 이슈에 대응하며, 일정 변경 사항을 재조정하거나 대체 자원을 투입하는 과정에서 전략적 판단 역량을 
            강화할 수 있습니다. 결국 자원관리 직무는 프로젝트 운영 전략을 실질적으로 수립하는 직무이기 때문에, 
            전략적 사고와 일정 관리 능력을 현장에서 가장 실질적으로 체득할 수 있는 직무입니다.


            <hr style="margin:35px 0; border:0; border-top: 1px solid #ddd;">

            <h4 style="font-weight:700; color:#444; margin-bottom:12px;">SNA 기반 직무 이동 분석이란?</h4>

            직무 추천은 단순히 경험 개수만으로 판단되지 않습니다.<br>
            조직 내에서 <b>어떤 직무가 다른 직무와 얼마나 연결되어 있고, 어떤 위치에 있는지</b>를 분석하는 것이 중요합니다.<br><br>

            이를 위해 본 리포트에서는 <b>SNA(Social Network Analysis, 사회 연결망 분석)</b> 기법을 활용합니다.<br><br>

            <img src="data:image/png;base64,{base64_image_string}" 
                style="width:100%; max-width:720px; border-radius:10px; display:block; margin:18px auto;">

            <div style="text-align:center; font-size:14px; color:#666; margin-top:6px;">
                ※ 공사 Track에서 프로젝트 관리 → 자원 관리로 이어지는 대표 이동 경로가 시각적으로 나타납니다.
        </div>
        """
        components.html(general_html, height=950, scrolling=True)

    # === Specialist Track ===
    with col2:
        # image_path = "/Users/airim/github/hari_fold_django/llm_hub/rpa_llm/assets/hari_testimage.png"
        image_path = os.path.join(BASE_DIR, "assets", "hari_testimage.png")
        img_html = ""
        try:
            with open(image_path, "rb") as img_file:
                import base64
                img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
                img_html = f'<img src="data:image/png;base64,{img_b64}" style="width:100%; border-radius:6px;">'
        except Exception as e:
            img_html = f"<p style='color:red;'>⚠️ 그래프 이미지를 불러오지 못했습니다: {e}</p>"

        specialist_html = f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px 20px;
            background-color: #fcfcfc;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            font-family: 'Inter','Segoe UI', sans-serif;
        ">
            <h3 style="color:#FFA571;text-align:center;">Specialist Track Report</h3>
            <p style="text-align:center;font-size:18px;margin-top:-8px;"><b>추천지수: 90%</b></p>

            <hr style="margin:10px 0;border-top:1px solid #eee;">
            <b>Specialist 추천 Logic</b><br>
            Specialist Track은 특정 직무 분야 내에서 깊이 있는 전문성을 가진 리더십을
            육성하기 위해, 직무 간 연계성과 전문성 발현 가능성을 기반으로 추천 직무를 도출합니다.

            <br><br>
            <h4 style="color:#FFA571;">{person_name}님의 경험 그래프</h4>
            {img_html}

            <br><br>
            <h4 style="color:#FFA571;">📌 Specialist 추천 직무</h4>
            <p><b>정열창님</b>에게 Specialist로 추천하는 직무는 <b>현장소장, PM</b>입니다.</p>

            <h5 style="margin-top:12px;color:#333;">1. 현장소장 경험</h5>
            <ul style="font-size:14px;">
                <li>프로젝트 달성과 성과 창출을 위한 강력한 리더십 발휘 기반 조성</li>
                <li>조직 전체의 리스크 관리 전략을 수립하고 실행하는 핵심 역할</li>
                <li>리스크 기반의 이슈 예방 및 해결 체계를 구축하며 <b>리스크·이슈 관리 능력 강화</b></li>
            </ul>

            <h5 style="margin-top:12px;color:#333;">2. PM 경험</h5>
            <ul style="font-size:14px;">
                <li>프로젝트 단계별 효율적 기획과 실행 전략 수립</li>
                <li>다양한 직무와 협업하며 팀 역할 조정 역량 강화</li>
                <li>전반적인 프로젝트 완료 역량 및 조정 능력 기를 수 있는 포지션</li>
            </ul>
        </div>
        """
        components.html(specialist_html, height=1000, scrolling=True)




