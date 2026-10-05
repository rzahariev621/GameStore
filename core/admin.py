from django.contrib import admin
from .models import Game, GameRequirement, VideoTutorial


admin.site.register(Game)
admin.site.register(GameRequirement)
admin.site.register(VideoTutorial)