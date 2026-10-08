from django import forms
from django.utils.translation import gettext_lazy as _

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

        labels = {
            'game': _('Game'),
            'title': _('Title'),
            'description': _('Description'),
            'video': _('Video'),
            'price': _('Price'),
        }


class GameForm(forms.ModelForm):
    class Meta:
        model = Game

        fields = [
            'title',
            'description',
            'release_date',
            'cover',
        ]

        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'release_date': _('Release date'),
            'cover': _('Cover'),
        }


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

        labels = {
            'minimum_cpu': _('Minimum CPU'),
            'minimum_gpu': _('Minimum GPU'),
            'minimum_ram_gb': _('Minimum RAM (GB)'),
            'minimum_storage': _('Minimum Storage'),
            'minimum_network': _('Minimum Network'),

            'recommended_cpu': _('Recommended CPU'),
            'recommended_gpu': _('Recommended GPU'),
            'recommended_ram_gb': _('Recommended RAM (GB)'),
            'recommended_storage': _('Recommended Storage'),
            'recommended_network': _('Recommended Network'),
        }


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

        labels = {
            'game': _('Game'),
            'title': _('Title'),
            'description': _('Description'),
            'video': _('Video'),
            'price': _('Price'),
            'status': _('Status'),
        }