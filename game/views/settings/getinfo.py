from django.http import JsonResponse
from game.models.player.player import Player


def getinfo_app(request):
    player = Player.objects.all()[0]  # 默认获取第一个用户的用户名和头像，方便调试
    # 返回一个字典
    return JsonResponse({
        'result': "success",
        'username': player.user.username,
        'photo': player.photo,
    })


def getinfo_web(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({
            'result': "not logined in",
        })
    else:
        player = Player.objects.get(user=user)
        return JsonResponse({
            'result': "success",
            'username': player.user.username,
            'photo': player.photo,
        })


def getinfo(request):
    platform = request.GET.get('platform') #判断不同平台，之后做不同处理
    if platform == "APP":
        return getinfo_app(request)
    else:
        return getinfo_web(request)


