"""
ASGI config for AI_mock_interviewer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from core.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_mock_interviewer.settings')

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#
#     # 👇 THIS IS THE FIX
#     "websocket": URLRouter(
#         websocket_urlpatterns
#     ),
# })

application = get_asgi_application()