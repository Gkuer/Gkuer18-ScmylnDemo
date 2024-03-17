from django.urls import path
from chatapp import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
]