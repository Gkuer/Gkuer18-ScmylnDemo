from django.shortcuts import render, get_object_or_404
from .models import Message, ChatRoom

def chat(request):
    rooms = ChatRoom.objects.all().order_by('-pk')
    return render(request, 'chatapp/chat.html', {'rooms': rooms})

def chat_room(request, room_name=None):
    room = get_object_or_404(ChatRoom, title=room_name)
    # 현재 채팅방에 속한 메시지만 필터링합니다.
    messages = Message.objects.filter(room=room).order_by('timestamp')
    # 필터링된 메시지와 채팅방 정보를 템플릿에 전달합니다.
    return render(request, 'chatapp/chat_room.html', {'room': room, 'messages': messages})