from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_video, name='upload_video'),
    path('process/<int:video_id>/', views.process_video, name='process_video'),
    path('result/<int:video_id>/', views.result, name='result'),
    path('ziatalks/', views.ziatalks_setup, name='ziatalks_setup'),
    path('ziatalks/chat/', views.ziatalks_chat, name='ziatalks_chat'),
]
