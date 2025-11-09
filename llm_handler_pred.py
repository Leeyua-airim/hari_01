# /llm_handler_pred.py
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_career_report(person_info: dict) -> dict:
    name = person_info.get("성명", "이름 없음")
    position = person_info.get("직급", "")
    dept = person_info.get("부서", "")
    g_score = person_info.get("G_score", None)
    s_score = person_info.get("S_score", None)
    history = person_info.get("Career_History", "")
    job = person_info.get("직무", "")

    prompt = f"""
    다음은 한 임직원의 경력 및 강점 데이터입니다.

    이름: {name}
    직무: {job}
    부서: {dept}
    직급: {position}

    제네럴리스트 점수: {g_score}
    스페셜리스트 점수: {s_score}

    커리어 이동 이력 (최근 15회):
    {history}

    이 정보를 기반으로 아래 지시를 따르세요:

    1️⃣ Generalist 경로에 맞는 CDP(경력개발계획) 제안을 3가지 HTML bullet 형식으로 작성하고,
    그 뒤에 이 경로의 핵심 요약 문단을 추가하세요.

    2️⃣ Specialist 경로에 맞는 CDP 제안을 3가지 HTML bullet 형식으로 작성하고,
    그 뒤에 이 경로의 핵심 요약 문단을 추가하세요.

    출력은 반드시 아래 JSON 형식으로 주세요:
    {{
    "general_track": "<HTML 형식 제안문>",
    "general_track_summary": "<제네럴 요약 문단>",
    "special_track": "<HTML 형식 제안문>",
    "special_track_summary": "<스페셜 요약 문단>"
    }}
    """

    # ✅ 최신 SDK 방식으로 호출
    response = client.chat.completions.create(
        model="gpt-4o",  # 또는 gpt-4o
        messages=[
            {"role": "system", "content": "너는 CJ 대한통운 건설부문의 HR 전문가이자 커리어 코치다."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )


    content = response.choices[0].message.content

    try:
        result = json.loads(content)
    
    except json.JSONDecodeError:
        # 혹시 모델이 JSON으로 안 줄 경우 대비
        result = {
            "general_track": "",
            "general_track_summary": "",
            "special_track": "",
            "special_track_summary": ""
        }
        # 기본적으로 마크다운 분리
        if "2️⃣" in content:
            result["general_track"] = content.split("2️⃣")[0]
        if "3️⃣" in content:
            parts = content.split("3️⃣")
            result["special_track"] = parts[1] if len(parts) > 1 else ""
        # 간단한 요약 추출
        result["general_track_summary"] = content[-300:]
        result["special_track_summary"] = content[-300:]

    return result