from django.urls import path, include

urlpatterns = [
    path("settings/", include('game.urls.settings.index')),  # 名称默认为项目路径，方便记忆
]
