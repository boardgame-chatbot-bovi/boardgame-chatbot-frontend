from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.home, name='home'),
    path('game-recommendation/', views.game_recommendation, name='game_recommendation'),
    path('gpt-rules/', views.gpt_rules, name='gpt_rules'),
    path('finetuning-rules/', views.finetuning_rules, name='finetuning_rules'),
    path('mobile/<str:chat_type>/', views.mobile_chat, name='mobile_chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/rule-summary/', views.rule_summary_api, name='rule_summary_api'),
    path('api/close-session/', views.close_session_api, name='close_session'),  # 세션 종료 API
    path('api/qr/<str:chat_type>/', views.generate_qr, name='generate_qr'),
    path('qa-stats/', views.qa_stats, name='qa_stats'),  # QA 통계 페이지
]
