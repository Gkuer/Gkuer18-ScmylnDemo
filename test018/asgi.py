"""
ASGI config for test018 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test018.settings')
django.setup()  # Django 환경 명시적으로 설정

import chatapp.routing  # Django 설정 로드 이후 임포트

import asyncio
from chatapp.consumers import reset_locations_periodically, check_overlap_periodically

# 주기적 작업 시작
loop = asyncio.get_event_loop()
loop.create_task(reset_locations_periodically())
loop.create_task(check_overlap_periodically())

# application = get_asgi_application()

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chatapp.routing.websocket_urlpatterns
        )
    ),
})