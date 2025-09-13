# urls.py
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Chat Sessions
    path('sessions/', views.ChatSessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<uuid:id>/', views.ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<uuid:session_id>/messages/', views.chat_session_messages, name='session-messages'),
    path('sessions/<uuid:session_id>/summary/', views.chat_summary, name='session-summary'),
    path('sessions/delete-all/', views.delete_all_sessions, name='delete-all-sessions'),
    
    # Messages
    path('send-message/', views.send_message, name='send-message'),
    
    # User Preferences  
    path('preferences/', views.UserChatPreferencesView.as_view(), name='user-preferences'),
]