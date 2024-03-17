from django.db import models

# Create your models here.

class ChatRoom(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)

# 메시지 모델
class Message(models.Model):
    content = models.TextField() # 메시지 내용
    timestamp = models.DateTimeField(auto_now_add=True) # 메시지 시간
    author = models.TextField(null=True, blank=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)