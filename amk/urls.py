from django.urls import path
from chatbot import views
from chatbot.meta_webhook import meta_webhook

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/chat/", views.chat, name="chat"),
    path("api/chat/history/<str:session_id>/", views.chat_history, name="chat_history"),
    path("api/leads/", views.leads, name="leads"),
    path("api/leads/<int:lead_id>/", views.lead_detail, name="lead_detail"),
    path("api/health/", views.health, name="health"),
    path("api/channels/", views.channels, name="channels"),
    path("webhooks/meta/", meta_webhook, name="meta_webhook"),
]
