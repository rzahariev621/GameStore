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

        widgets = {
            'game': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                }
            ),

            'video': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                }
            ),
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

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                }
            ),

            'release_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                },
                format='%Y-%m-%d',
            ),

            'cover': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),
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

        widgets = {
            'minimum_cpu': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'minimum_gpu': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'minimum_ram_gb': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                }
            ),

            'minimum_storage': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'minimum_network': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'recommended_cpu': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'recommended_gpu': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'recommended_ram_gb': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                }
            ),

            'recommended_storage': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'recommended_network': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),
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

        widgets = {
            'game': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                }
            ),

            'video': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0',
                }
            ),

            'status': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
        }