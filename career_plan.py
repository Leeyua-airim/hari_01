# # career_plan.py
# import re
# import pandas as pd
# import numpy as np

# ALIAS = {"교육과정": "교육"}

# def clean_job_name(name: str) -> str:
#     cleaned = re.sub(
#         r'\b(Associate|Manager|Specialist|Leader|Sr\.?\s?Leader|Executive|Director|Professional)\b',
#         '', name, flags=re.IGNORECASE
#     ).strip()
#     return ALIAS.get(cleaned, cleaned)

# def recommend_general_track_with_preparedness(employee_id, emp_data, mapping_data, similarity_matrix):
#     emp_row = emp_data[emp_data['EMPLID'] == employee_id]
#     if emp_row.empty:
#         return None

#     job_cols = [c for c in emp_data.columns if "_발령_직무" in c]
#     day_cols = [c for c in emp_data.columns if "재직일수" in c]

#     jobs = emp_row[job_cols].values.flatten()
#     days = emp_row[day_cols].values.flatten()
#     pairs = [(clean_job_name(str(j)), float(d)) for j, d in zip(jobs, days)
#              if pd.notna(j) and pd.notna(d)]

#     job_to_core = dict(zip(mapping_data["유사직무"], mapping_data["핵심직무"]))
#     mapped = [(job_to_core[j], d) for j, d in pairs if j in job_to_core]
#     if not mapped:
#         return None

#     core_days = (pd.DataFrame(mapped, columns=["핵심직무", "근무일수"])
#                    .groupby("핵심직무")["근무일수"].sum())

#     all_cores = list(similarity_matrix.columns)
#     experienced = list(core_days.index)
#     unexperienced = [j for j in all_cores if j not in experienced]

#     preparedness = {}
#     for uj in unexperienced:
#         total_score, total_weight = 0.0, 0.0
#         for cj, d in core_days.items():
#             if cj in similarity_matrix.index and uj in similarity_matrix.columns:
#                 total_score += d * float(similarity_matrix.loc[cj, uj])
#                 total_weight += d
#         if total_weight > 0:
#             preparedness[uj] = total_score / total_weight

#     if not preparedness:
#         return None

#     scores_sorted = sorted(preparedness.values(), reverse=True)
#     top_cut = np.percentile(scores_sorted, 70)
#     mid_cut = np.percentile(scores_sorted, 40)

#     long_term = [k for k, v in preparedness.items() if v >= top_cut]
#     early_term = [k for k, v in preparedness.items() if mid_cut <= v < top_cut]
#     mid_term  = [k for k, v in preparedness.items() if v < mid_cut]

#     return {
#         "현재_핵심직무": experienced,
#         "준비도_점수": preparedness,
#         "초기": early_term,
#         "중기": mid_term,
#         "장기": long_term
#     }


# def format_preparedness_table(preparedness_dict: dict) -> str:
#     """준비도 점수를 HTML 표로 예쁘게 변환 (중앙정렬 + 테두리 포함)"""
#     if not preparedness_dict:
#         return "<p style='font-size:13px; color:#999;'>준비도 데이터가 없습니다.</p>"

#     df = pd.DataFrame(preparedness_dict.items(), columns=["핵심직무", "준비도점수"])
#     df = df.sort_values("준비도점수", ascending=False)

#     # ✅ HTML 테이블 스타일링
#     table_html = """
#     <table style='width:100%; border-collapse:collapse; font-size:12.5px; border:1px solid #ddd;'>
#         <thead>
#             <tr style='background-color:#f0f3ff; color:#1a3cff; text-align:center;'>
#                 <th style='padding:8px; border:1px solid #ddd;'>핵심직무</th>
#                 <th style='padding:8px; border:1px solid #ddd;'>준비도점수</th>
#             </tr>
#         </thead>
#         <tbody>
#     """

#     for _, row in df.iterrows():
#         table_html += f"""
#         <tr style='text-align:center;'>
#             <td style='padding:6px; border:1px solid #ddd;'>{row['핵심직무']}</td>
#             <td style='padding:6px; border:1px solid #ddd;'>{row['준비도점수']:.2f}</td>
#         </tr>
#         """

#     table_html += "</tbody></table>"
#     return table_html
