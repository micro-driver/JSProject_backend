from django.urls import path
from game.views.settings.getinfo import getinfo
from game.views.settings.login import signin
from game.views.settings.logout import signout
from game.views.settings.register import register

urlpatterns = [
    path("getinfo/", getinfo, name="setting_getinfo"),  # 名称默认为项目路径，方便记忆
    path("login/", signin, name="settings_login"),
    path("logout/", signout, name="settings_logout"),
    path("register/", register, name="settings_register"),
]