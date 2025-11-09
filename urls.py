from django.urls import path
from . import views

app_name = "pred_llm"

urlpatterns = [
    path("", views.pred_page, name="pred_page"),  # /llm_hub/reader/
]
