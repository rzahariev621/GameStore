from django import forms
from .models import VideoTutorial, Game, GameRequirement


class VideoTutorialForm(forms.ModelForm):
    class Meta:
        model = VideoTutorial

        fields = [
            'game',
            'title',
            'description',
            'video',
            'price',
        ]



class GameForm(forms.ModelForm):
    class Meta:
        model = Game

        fields = [
            'title',
            'description',
            'release_date',
            'cover',
        ]



class GameRequirementForm(forms.ModelForm):
    class Meta:
        model = GameRequirement

        fields = [
            'minimum_cpu',
            'minimum_gpu',
            'minimum_ram_gb',
            'minimum_storage',
            'minimum_network',

            'recommended_cpu',
            'recommended_gpu',
            'recommended_ram_gb',
            'recommended_storage',
            'recommended_network',
        ]



class AdminTutorialForm(forms.ModelForm):
    class Meta:
        model = VideoTutorial

        fields = [
            'game',
            'title',
            'description',
            'video',
            'price',
            'status',
        ]