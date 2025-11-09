from django.shortcuts import render

def pred_page(request):
    # Streamlit Pred 앱의 포트로 연결
    return render(request, "llm_hub/pred.html", {
        "streamlit_url": "http://127.0.0.1:8502/?embed=true"
    })
