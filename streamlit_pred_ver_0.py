# import streamlit as st
# import pandas as pd
# from rapidfuzz import process, fuzz
# import os
# import base64
# import os, sys, io, re
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# from llm_hub.pred_llm.llm_handler_pred import generate_career_report
# from llm_hub.pred_llm.career import format_career_as_table
# from llm_hub.pred_llm.career_plan import recommend_general_track_with_preparedness, format_preparedness_table
# import streamlit.components.v1 as components
# from llm_hub.pred_llm.specialist_track_score import build_specialist_graph_for_streamlit


# # ---- 페이지 설정 ----
# st.set_page_config(page_title="CDP 가이드 생성기", layout="wide")

# # ---- 데이터 로드 ----
# EMPLOYEE_PATH = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only인사.xlsx"
# SCORE_PATH    = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_specialist_generalist_score_result.xlsx"
# CAREER_PATH   = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_발령정보_result.xlsx"
# LOGO_PATH     = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/assets/cj_company.png"

# EMP_PATH = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/only_발령정보.xlsx"
# MAP_PATH = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/핵심직무_유사직무_매핑.xlsx"

# emp_data = pd.read_excel(EMP_PATH, dtype={'EMPLID': str})
# mapping_data = pd.read_excel(MAP_PATH)

# # 유사도 행렬 상수
# similarity_matrix = pd.DataFrame({
#     "고객 관리": [10,6.5,6,4.5,5,5,5,2,4,6.15],
#     "계약 및 협상": [5.5,10,4,3,4.5,6,3,2.5,2.5,4.3],
#     "경영관리": [4,5,10,8,5,5,3,3.5,3.5,4.5],
#     "재무": [3.5,6,8,10,4.5,6,2,1,2.5,3],
#     "인력 확보 유지 및 육성": [4.5,5.5,6.5,2.5,10,5,1.5,5,3.5,5.5],
#     "컴플라이언스": [4,7.5,4,3,5,10,2,5,2.5,4.85],
#     "자원 관리": [6.5,2.5,3,1.5,4.5,5,10,6,4.5,5.15],
#     "안전경영": [2,2.5,4.5,1,7.5,5.5,3,10,6.5,4.5],
#     "스마트 건설": [4,3,4,2,5.5,3.5,6,6.5,10,5.65],
#     "프로젝트 관리": [7.85,5.85,4.8,3.15,7,4.65,7.5,8.15,6.65,10]
# }, index=["고객 관리","계약 및 협상","경영관리","재무","인력 확보 유지 및 육성","컴플라이언스","자원 관리","안전경영","스마트 건설","프로젝트 관리"])



# # ---- 로고 로드 ----
# def image_to_base64(path):
#     with open(path, "rb") as f:
#         return base64.b64encode(f.read()).decode()

# logo_b64 = image_to_base64(LOGO_PATH)

# # ---- 데이터 파일 존재 여부 확인 ----
# if not os.path.exists(EMPLOYEE_PATH):
#     st.error(f"데이터 파일을 찾을 수 없습니다: {EMPLOYEE_PATH}")
#     st.stop()

# # ---- 개별 데이터 읽기 ----
# employee_df = pd.read_excel(EMPLOYEE_PATH)
# score_df    = pd.read_excel(SCORE_PATH)
# career_df   = pd.read_excel(CAREER_PATH)

# # ---- 이름 정규화 (공통 함수) ----
# def normalize_name(series):
#     """성명 컬럼의 공백, 개행, 탭 제거"""
#     return series.astype(str).str.replace(r"\s+", "", regex=True).str.strip()

# employee_df["성명"] = normalize_name(employee_df["성명"])
# score_df["성명"]    = normalize_name(score_df["성명"])
# career_df["성명"]   = normalize_name(career_df["성명"])



# # ---- 데이터 병합 ----
# # (컬럼 존재 여부 확인은 병합 전에 한 번만!)
# missing_cols = [c for c in ["G_score", "S_score"] if c not in score_df.columns]
# if missing_cols:
#     st.warning(f"⚠️ 결과 파일에 {', '.join(missing_cols)} 컬럼이 없습니다. 계산 스크립트를 다시 실행하세요.")
# else:
#     merged_df = (
#         employee_df
#         .merge(score_df[["성명", "G_score", "S_score"]], on="성명", how="left")
#         .merge(career_df[["성명", "Career_History"]], on="성명", how="left")
#     )


# # ---- 필수 컬럼 체크 ----
# required_cols = ["성명", "직군", "부서", "직급", "직무", "포지션", "경력경로"]
# for col in required_cols:
#     if col not in merged_df.columns:
#         st.error(f"⚠️ '{col}' 컬럼이 없습니다. 데이터 컬럼명을 확인해주세요.")
#         st.stop()
        
# def get_recent_career_history(name, max_records=10):
#     """특정 인물의 최근 발령 이력 10개를 문자열로 반환"""
#     row = career_df[career_df["성명"] == name]
#     if row.empty:
#         return "발령 이력 없음"
#     history_str = str(row.iloc[0]["Career_History"]).strip()
#     if not history_str or history_str.lower() == "nan":
#         return "발령 이력 없음"

#     parts = [p.strip() for p in history_str.split("→") if p.strip()]
#     recent = " → ".join(parts[-max_records:])
#     return recent




# # ---- CSS ----
# st.markdown(f"""
#     <style>
#     /* Header */
#     .header-container {{
#     display: flex;
#     flex-direction: column;
#     align-items: center;
#     text-align: center;
#     margin-top: 20px;
#     margin-bottom: 25px;
#     }}
#     .header-title-text {{
#     font-size: 26px;
#     font-weight: 600;
#     font-family: "Segoe UI", "Helvetica Neue", sans-serif;
#     font-style: normal;
#     background: linear-gradient(90deg, #0059ff 0%, #00c6ff 100%);
#     -webkit-background-clip: text;
#     -webkit-text-fill-color: transparent;
#     }}

#     /* Card List Layout */
#     .card-list {{
#     display: flex;
#     flex-direction: column;
#     gap: 12px;
#     margin-top: 15px;
#     margin-bottom: 30px;
#     }}

#     /* Card Button (Streamlit button styled as card) */
#     .card-button > button {{
#     display: flex;
#     align-items: center;
#     gap: 14px;
#     background-color: #ffffff;
#     border-radius: 12px;
#     border: 1px solid #e5e8ff;
#     box-shadow: 0 2px 4px rgba(0,0,0,0.04);
#     padding: 14px 18px;
#     width: 100%;
#     text-align: left;
#     transition: all 0.25s ease-in-out;
#     font-size: 15px;
#     color: #222;
#     }}
#     .card-button > button:hover {{
#         background-color: #f4f7ff;
#         transform: translateY(-2px);
#         box-shadow: 0 4px 12px rgba(0,0,0,0.08);
#         border-color: #b6c4ff;
#         color: #1a3cff;
#     }}
#     .card-selected > button {{
#         border: 2px solid #1a3cff !important;
#         background-color: #f0f3ff !important;
#         color: #1a3cff !important;
#     }}
#     .card-logo {{
#         width: 36px;
#         height: 36px;
#         border-radius: 50%;
#         object-fit: cover;
#     }}
#     </style>
#     """, unsafe_allow_html=True)

# # ---- Header ----
# st.markdown("""
# <div class="header-container">
#     <div class="header-title-text">Career Development Plan (CDP)</div>
# </div>
# """, unsafe_allow_html=True)

# # ---- 상태 관리 ----
# if "selected_person" not in st.session_state:
#     st.session_state.selected_person = None

# # ---- 검색 입력 ----
# ser_col1, ser_col2, ser_col3 = st.columns([3, 2, 3])  # 1:2:1 비율로 가운데 열만 사용
# with ser_col2:
#     search_name = st.text_input(
#         "",
#         placeholder="CDP 조회가 필요한 임직원 성함을 입력해주세요.",
#         label_visibility="collapsed"
#     )
# if search_name.strip():
#     all_names = merged_df["성명"].dropna().astype(str).unique().tolist()
#     matches = process.extract(search_name, all_names, scorer=fuzz.WRatio, limit=6)

#     if matches:
#         st.write('\n\n')
#         st.markdown(
#             "<h4 style='text-align:center; margin-top:20px;'>검색결과 기반 임직원 추천</h4>",
#             unsafe_allow_html=True
#         )
#         st.markdown('<div class="card-list">', unsafe_allow_html=True)

#         # ✅ 3개씩 끊어서 2행 구성
#         for i in range(0, len(matches), 3):
#             row_matches = matches[i:i+3]
#             cols = st.columns(len(row_matches))

#             for j, (match, score, _) in enumerate(row_matches):
#                 person = merged_df[merged_df["성명"] == match].iloc[0]
#                 selected = (st.session_state.selected_person == match)

#                 with cols[j]:
#                     # ---- 카드 정보 (상단) ----
#                     st.markdown(f"""
#                     <div class="name-card" style="display:flex;align-items:center;flex-direction:column;
#                                 justify-content:center;text-align:center;padding:10px 0 5px 0;">
#                         <img src="data:image/png;base64,{logo_b64}" class="card-logo" 
#                              style="width:48px;height:48px;margin-bottom:6px;">
#                         <div style="font-weight:600;color:#2342ff;">{match}</div>
#                         <div style="color:#555;font-size:13px;">
#                             {person['하위영역명']} | {person['직군']} | {person['직급']}
#                         </div>
#                     </div>
#                     """, unsafe_allow_html=True)

#                     # ---- 버튼 (하단 중앙 정렬) ----
#                     btn_left, btn_center, btn_right = st.columns([1, 2, 1])
#                     with btn_center:
#                         clicked = st.button(
#                             f"**{match}님**의 CDP 리포트 생성하기",
#                             key=f"btn_{match}",
#                             help=f"{match} 선택됨"
#                         )
                    
#                     # 여기서 선택된 사람의 세션스테이스 생성
#                     if clicked:
#                         st.session_state.selected_person = match

#         st.markdown("</div>", unsafe_allow_html=True)
#     else:
#         st.warning("일치하거나 유사한 이름을 찾지 못했습니다.")


#     # ---- 리포트 출력 ----
#     # 선택된 인물이 있을 때
#     if st.session_state.selected_person:
#         person_name = st.session_state.selected_person
#         person_info = merged_df[merged_df["성명"] == person_name].iloc[0].to_dict()
#         career_summary = get_recent_career_history(person_name)
#         career_table_html = format_career_as_table(career_summary)
        
#         # --- 제네럴 트랙 준비도 추천 ---
#         emplid = str(person_info.get("EMPLID", ""))

#         track_result = recommend_general_track_with_preparedness(
#             emplid, emp_data, mapping_data, similarity_matrix
#         )

        
#         # generalist specialist 계산
#         g_score = person_info.get("G_score", None)
#         s_score = person_info.get("S_score", None)
    
#         # 안전 포맷 함수
#         def fmt(x):
#             return "N/A" if pd.isna(x) else f"{x:.2f}"
    
#         # ---- GPT 리포트 생성 ----
#         with st.spinner("🔄 CDP 리포트를 생성 중입니다..."):
#             # report = generate_career_report(person_info)
#             st.divider()
    
#             # 헤더 표시
#             st.markdown(f"""
#                 <div style="text-align:center; margin:25px 0 20px 0;">
#                     <h3 style="font-weight:600; color:#2a2a2a; letter-spacing:-0.2px; margin-bottom:6px;">
#                         {person_name}님의 CDP 가이드 리포트
#                     </h3>
#                     <p style="font-size:13px; color:#6c6c6c; margin:0; font-weight:400;">
#                         Career Development Plan Overview
#                     </p>
#                 </div>
#             """, unsafe_allow_html=True)
    
#         # ---- 두 트랙 표시 ----
#         col1, col2 = st.columns(2)    
#         # 제네럴 트랙
#         with col1:
#         # --- 제네럴 트랙 카드 전체를 components.html로 교체 ---
#             # --- 제네럴 트랙 (스페셜 트랙과 동일한 UI 스타일) ---
#             if track_result:
#                 prep_html = format_preparedness_table(track_result["준비도_점수"])
#                 early = ", ".join(track_result["초기"]) or "없음"
#                 mid = ", ".join(track_result["중기"]) or "없음"
#                 long = ", ".join(track_result["장기"]) or "없음"
#                 current_core = ", ".join(track_result["현재_핵심직무"])         

#                 general_html = f"""
#                 <div style="
#                     border: 1px solid #ddd;
#                     border-radius: 8px;
#                     padding: 15px 20px;
#                     background-color: #fcfcfc;
#                     box-shadow: 0 1px 3px rgba(0,0,0,0.03);
#                     font-family: 'Segoe UI', sans-serif;
#                 ">
#                     <h3 style="
#                         color:#1a3cff;
#                         margin-bottom:10px;
#                         text-align:center;
#                     ">
#                         General Track Report<br>
#                         <span style="color:#777; font-size:18px; text-align:center; margin-bottom:6px;">
#                             추천지수: {fmt((g_score or 0)*100)}%
#                         </span>
#                     </h3>           

#                     <p style="
#                         text-align:center;
#                         font-weight:700;
#                         font-size:15px;
#                         color:#1a3cff;
#                         margin-bottom:6px;
#                     ">
#                         과거 경험 디브리핑
#                     </p>
#                     {career_table_html}         

#                     <hr style="margin:15px 0; border:none; border-top:1px solid #e0e0e0;">          

#                     <p style="
#                         text-align:center;
#                         font-weight:700;
#                         font-size:15px;
#                         color:#1a3cff;
#                         margin-bottom:10px;
#                     ">
#                         핵심직무 및 준비도 기반의 커리어 추천
#                     </p>            

#                     <div style="
#                         font-size:12.5px;
#                         color:#555;
#                         background-color:#f7f8fb;
#                         border-radius:6px;
#                         padding:8px 10px;
#                         border-left:4px solid #1a3cff;
#                         margin-bottom:10px;
#                     ">
#                         <b>🔍 커리어 추천 로직 설명</b><br>
#                         본 알고리즘은 임직원의 과거 <b>발령 직무 및 근무기간</b> 데이터를 기반으로 
#                         각 <b>핵심직무 간 유사도(similarity)</b>를 계산하여<br> 
#                         직무별 <b>준비도(Preparedness)</b>를 산출합니다.<br><br>
#                         <b>준비도(Preparedness)</b>란, <br>각 핵심직무에 대해 
#                         본인이 과거 수행한 경험(근무기간)에 
#                         직무간 유사도를 가중하여 계산한 지표입니다. <br>
#                         점수가 높을수록 해당 직무로의 전환 및 성장 가능성이 높음을 의미합니다.

#                     </div>


#                     <div style="font-size:13px; color:#333; margin-bottom:10px;">
#                         <b>현재 핵심직무 경험:</b> {current_core}
#                     </div>          

#                     <div style="margin-top:10px;">
#                         {prep_html}
#                     </div>     
#                     <br>
#                     <br>
                    
#                     <div style="
#                         text-align:center;
#                         margin-bottom:8px;
#                         border-bottom:1px solid #dce3ff;
#                         padding-bottom:6px;
#                     ">
#                         <span style="
#                             font-size:14px;
#                             color:#1a3cff;
#                             font-weight:900;
#                             letter-spacing:-0.2px;
#                         ">
#                             분석 및 예측 기반의 커리어 추천
#                         </span>
#                     </div>

#                     <div style="
#                         font-size:12.5px;
#                         color:#555;
#                         background-color:#f9f9f9;
#                         border-radius:6px;
#                         padding:8px 10px;
#                         border-left:4px solid #1a3cff;
#                         margin-bottom:12px;
#                     ">
#                         <b>제네럴 트랙 커리어 추천 방식</b><br>
#                         준비도 점수를 기준으로 직무별 성장 가능성을 예측합니다.<br><br>
#                         🔵 <b>높은 점수대</b>는 단기간 내 전환이 가능한 유망 영역,<br>
#                         🟢 <b>중간 점수대</b>는 역량 강화 후 도전이 필요한 영역,<br>
#                         🟡 <b>낮은 점수대</b>는 장기적으로 성장할 핵심 목표 영역이 됩니다. 
#                     </div>

#                     <div style="margin-top:15px; font-size:13px;">
#                         <div style="
#                             display: flex;
#                             flex-direction: column;
#                             gap: 10px;
#                             margin-top: 10px;
#                             background-color: #f8f9ff;
#                             border-radius: 8px;
#                             padding: 12px 14px;
#                             border: 1px solid #e4e7ff;
#                         ">
#                             <div style="display:flex; flex-direction:column;">
#                                 <div style="display:flex; align-items:center; margin-bottom:4px;">
#                                     <span style="font-size:16px; margin-right:6px;">🔵</span>
#                                     <b style="color:#3498DB;">장기 추천/초기 추천</b>
#                                     <span style="font-size:12px; color:#777; margin-left:8px;">(단기간 내 확장 가능한 직무)</span>
#                                 </div>
#                                 <div style="margin-left:25px; color:#333;">{early}</div>
#                             </div>

#                             <div style="display:flex; flex-direction:column;">
#                                 <div style="display:flex; align-items:center; margin-bottom:4px;">
#                                     <span style="font-size:16px; margin-right:6px;">🟢</span>
#                                     <b style="color:#008000;">중기 추천</b>
#                                     <span style="font-size:12px; color:#777; margin-left:8px;">(중간 수준의 유사도를 가진 성장 영역)</span>
#                                 </div>
#                                 <div style="margin-left:25px; color:#333;">{mid}</div>
#                             </div>

#                             <div style="display:flex; flex-direction:column;">
#                                 <div style="display:flex; align-items:center; margin-bottom:4px;">
#                                     <span style="font-size:16px; margin-right:6px;">🟡</span>
#                                     <b style="color:#F1C40F;">장기 추천</b>
#                                     <span style="font-size:12px; color:#777; margin-left:8px;">(장기적 관점에서 도전 가능한 직무)</span>
#                                 </div>
#                                 <div style="margin-left:25px; color:#333;">{long}</div>
#                             </div>
#                         </div>
#                     </div>
            
#                 </div>
#                 """         

#                 # ✅ components.html 로 깨짐 없는 렌더링
#                 components.html(general_html, height=1200, scrolling=True)


#         # --- 스페셜 트랙 (col2)
#         from streamlit import components
#         def infer_special_track(job_name: str) -> str:
#             """
#             직무명(예: '인사담당', '건축시공', '전략기획')을 기반으로
#             specialist_track_interview 내 트랙을 유추.
#             """
#             job_name = str(job_name).strip()

#             # 트랙별 키워드 매핑 (데이터 기반 업데이트)
#             mapping = {
#                 # 공사 관련
#                 "공사": "공사 Track",
#                 "시공": "공사 Track",
#                 "건축": "공사 Track",
#                 "건설": "공사 Track",
#                 "설비": "공사 Track",
#                 "PE": "공사 Track",
#                 "견적": "공사 Track",
#                 "전기": "공사 Track",

#                 # 기술 관련
#                 "기술": "기술 Track",
#                 "기획": "기술 Track",
#                 "원가": "기술 Track",
#                 "공사지원": "기술 Track",

#                 # 경영지원 관련
#                 "경영": "경영지원 Track",
#                 "전략": "경영지원 Track",
#                 "재무": "경영지원 Track",
#                 "기획": "경영지원 Track",
#                 "법무": "경영지원 Track",
#                 "DT": "경영지원 Track",
#                 "혁신": "경영지원 Track",

#                 # 인사 관련
#                 "인사": "인사 Track",
#                 "교육": "인사 Track",
#                 "경영진단": "인사 Track",

#                 # 안전 관련
#                 "안전": "안전경영 Track",
#                 "법무/컴플라이언스": "안전경영 Track",
#                 "운영": "안전경영 Track",

#                 # 영업 관련
#                 "영업": "영업 Track",
#                 "개발영업": "영업 Track",
#                 "공공영업": "영업 Track",
#                 "민간영업": "영업 Track",

#                 # 환경사업 관련
#                 "환경": "환경사업 Track",
#                 "환경사업": "환경사업 Track",
#                 "환경설계": "환경사업 Track",
#                 "환경영업": "환경사업 Track",
#                 "인프라영업": "환경사업 Track",
#             }

#             for k, v in mapping.items():
#                 if k in job_name:
#                     return v

#             return "기타"
#         def fig_to_base64_safe(fig):
#             """
#             matplotlib Figure → base64 PNG 변환 (Streamlit-safe)
#             macOS/한글 폰트/Streamlit rerun 환경에서도 깨지지 않음
#             """
#             try:
#                 import io, base64, matplotlib

#                 # ⚙️ 렌더러를 Agg로 미리 변경 (macOS 한글, Streamlit 환경 대응)
#                 matplotlib.use("Agg")

#                 # Figure 객체가 유효한지 검사
#                 if fig is None:
#                     return ""

#                 # Streamlit rerun 대비: Figure 강제 draw
#                 fig.canvas.draw_idle()

#                 buf = io.BytesIO()
#                 fig.savefig(
#                     buf,
#                     format="png",
#                     dpi=150,
#                     bbox_inches="tight",
#                     facecolor="white",
#                 )
#                 buf.seek(0)
#                 img_b64 = base64.b64encode(buf.read()).decode("utf-8")
#                 buf.close()
#                 return img_b64
#             except Exception as e:
#                 import traceback
#                 print("⚠️ base64 변환 오류:", e)
#                 traceback.print_exc()
#                 return ""
        
        
#         with col2:
#             # 1) 그래프 데이터 준비
#             data_path = "/Users/airim/github/hari_fold_django/llm_hub/pred_llm/data/specialist_track_interview.xlsx"
#             graphs = build_specialist_graph_for_streamlit(data_path)

#             user_job = person_info.get("직무", "")
#             inferred_track = infer_special_track(user_job)

#             # 2) 트랙 폴백: 없으면 첫 번째 트랙으로 대체
#             track_for_view = inferred_track if inferred_track in graphs else (list(graphs.keys())[0] if graphs else None)

#             img_html = ""
#             top_roles_html = ""
#             track_caption = ""

#             if track_for_view:
#                 fig = graphs[track_for_view]["figure"]
#                 centrality_df = graphs[track_for_view]["중심성"].copy()

#                 # base64 변환
#                 img_b64 = fig_to_base64_safe(fig)

#                 # 3) 중심성 TOP3 설명
#                 role_lines = []

#             # enumerate로 TOP3 생성 (위의 itertuples 교체)
#             if track_for_view:
#                 top3 = graphs[track_for_view]["중심성"].head(3)
#                 role_lines = []
#                 for i, row in enumerate(top3.itertuples(index=False), start=1):
#                     job = getattr(row, "직무")
#                     degree = float(getattr(row, "Degree"))
#                     betweenness = float(getattr(row, "Betweenness"))

#                     if degree > 0.6 and betweenness > 0.4:
#                         role = "조직 내 핵심 연결 허브 역할을 수행합니다."
#                     elif degree > 0.5:
#                         role = "다양한 직무와 폭넓게 협력하는 역할입니다."
#                     elif betweenness > 0.4:
#                         role = "조직 간 브릿지(연결점) 역할을 담당합니다."
#                     else:
#                         role = "전문 영역 중심의 직무 역할입니다."

#                     role_lines.append(
#                         f"<li><b>{job}</b> — {role} "
#                         f"<span style='color:#999; font-size:12px;'>(연결 {degree:.2f}, 매개 {betweenness:.2f})</span></li>"
#                     )

#                 top_roles_html = """
#                 <ol style="
#                     padding-left: 22px;
#                     margin-top: 6px;
#                     line-height: 1.6;
#                     color: #333;
#                     font-size: 13px;
#                 ">
#                 """ + "".join(role_lines) + "</ol>"

#                 # 4) 이미지 HTML (폴백 처리)
#                 if img_b64:
#                     img_html = f'<img src="data:image/png;base64,{img_b64}" style="width:100%; border-radius:6px; margin-top:10px;">'
#                 else:
#                     # base64 실패 → 카드 아래 즉시 시각 확인용 폴백
#                     img_html = "<div style='color:#c00; font-size:12px;'>⚠️ 그래프 이미지를 생성하지 못했습니다. 아래 임시 폴백으로 표시합니다.</div>"

#                 # 현재 직무로 매칭된 트랙/폴백 트랙 안내
#                 if inferred_track != track_for_view:
#                     track_caption = f"<div style='font-size:12px; color:#777; text-align:center;'>* '{inferred_track}' 트랙 데이터가 없어 '{track_for_view}'로 대체 표시</div>"

#             # 5) 카드 HTML
#             special_html = f"""
#             <div style="
#                 border: 1px solid #ddd;
#                 border-radius: 8px;
#                 padding: 15px 20px;
#                 background-color: #fcfcfc;
#                 box-shadow: 0 1px 3px rgba(0,0,0,0.03);
#                 font-family: 'Segoe UI', sans-serif;
#             ">
#                 <h3 style="
#                     color:#FFA571;
#                     margin-bottom:10px;
#                     text-align:center;
#                 ">
#                     Special Track Report<br>
#                     <span style="color:#777; font-size:18px;">
#                         추천지수: {fmt((s_score or 0)*100)}%
#                     </span>
#                 </h3>
            
#                 <p style="text-align:center; font-weight:700; font-size:15px; color:#FFA571;">
#                     과거 경험 디브리핑
#                 </p>
#                 {career_table_html}
            
#                 <hr style="margin:15px 0; border:none; border-top:1px solid #eee;">
            
#                 <h4 style="text-align:center; color:#FFA571;">CDP 성공 가이드 SNA</h4>
            
#                 {track_caption}
            
#                 <!-- 스페셜 트랙 CDP TOP3 -->
#                 <div style="margin-top:15px; font-size:13px; color:#333; text-align:left;">
#                     <b style="display:block; color:#FFA571; margin-bottom:5px;">핵심 연결 직무 TOP 3</b>
#                     {top_roles_html if top_roles_html else "<div style='color:#999;'>표시할 데이터가 없습니다.</div>"}
#                 </div>
            
#                 <!-- 💡 그래프 읽는 법 안내 -->
#                 <div style="
#                     font-size:12.5px;
#                     color:#555;
#                     background-color:#f7f8fb;
#                     border-radius:6px;
#                     padding:8px 10px;
#                     border-left:4px solid #FFA571;
#                     margin-top:10px;
#                     margin-bottom:15px;
#                 ">
#                     <b>💡 그래프 읽는 법 안내</b><br>
#                     <b>연결(Degree Centrality)</b>이 높을수록 많은 직무와 직접적인 관계를 맺고 있는 ‘허브’ 역할을 의미합니다.<br>
#                     <b>매개(Betweenness Centrality)</b>가 높을수록 서로 다른 직무 간 연결을 이어주는 ‘브릿지’ 역할을 의미합니다.<br><br>
#                     따라서 <b>두 지표 모두 높은 직무</b>를 순차적으로 수행하는 것이 스페셜 트랙의 CDP 가 됩니다
#                 </div>
            
#                 <!-- 네트워크 그래프 -->
#                 <div style="margin-top:10px;">
#                     {img_html}
#                 </div>
#             </div>
#             """
                    


#             # 6) 렌더링
#             components.v1.html(special_html, height=1200, scrolling=True)

#             # 7) base64 실패 폴백: 카드 밖에 즉시 그려서 확인
#             if track_for_view and not img_b64:
#                 st.pyplot(graphs[track_for_view]["figure"], clear_figure=True)